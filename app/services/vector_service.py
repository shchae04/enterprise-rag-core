import google.generativeai as genai
import asyncio
from typing import List, Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, or_

from app.core.config import settings
from app.core.logging import logger
from app.models.embedding import Embedding
from app.utils.nlp import extract_nouns

# Configure Gemini
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)

EMBEDDING_MODEL = "models/text-embedding-004"
CATEGORIES = ['매뉴얼', '가이드', '포워더 질의응답', 'ENS', 'AMS', 'ACI', '웹페이지', '기술문서', '기타']

class VectorService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @staticmethod
    async def create_embedding(text: str) -> List[float]:
        """Gemini text-embedding-004를 사용하여 텍스트 임베딩 생성 (Async wrapper with Thread)"""
        try:
            # genai.embed_content는 동기 함수이므로, 이벤트 루프 차단을 막기 위해 스레드에서 실행
            result = await asyncio.to_thread(
                genai.embed_content,
                model=EMBEDDING_MODEL,
                content=text,
                task_type="retrieval_document"
            )
            return result['embedding']
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []
            
    # Static method wrapper for backward compatibility or direct use
    @staticmethod
    async def create_embedding_static(text: str) -> List[float]:
        return await VectorService.create_embedding(text)

    @staticmethod
    async def classify_content(title: str, content_preview: str) -> str:
        """Gemini를 사용하여 콘텐츠 카테고리 자동 분류"""
        try:
            # Use the lite model for fast classification
            model = genai.GenerativeModel(settings.LLM_MODEL)
            prompt = f"""
            다음 문서를 아래 카테고리 중 하나로 분류해주세요:
            {', '.join(CATEGORIES)}

            제목/파일명: {title}
            내용 미리보기:
            {content_preview[:1000]}

            위 문서가 어떤 카테고리에 속하는지 카테고리 이름만 정확히 답변해주세요.
            반드시 제공된 카테고리 중 하나를 선택해야 합니다.
            """
            response = await model.generate_content_async(prompt)
            category = response.text.strip()
            
            if category in CATEGORIES:
                return category
            for cat in CATEGORIES:
                if cat in category:
                    return cat
            return "기타"
        except Exception as e:
            logger.warning(f"Category classification failed: {e}, utilizing default '기타'")
            return "기타"

    async def search_hybrid(self, query: str, top_k: int = 5) -> List[Embedding]:
        """
        하이브리드 검색: Vector Search + Keyword Search (Full-Text)
        Reciprocal Rank Fusion (RRF) 알고리즘 사용
        """
        # 1. Generate Query Embedding
        query_embedding = await self.create_embedding(query)
        if not query_embedding:
            return []

        # Retrieve significantly more candidates for RRF to ensure recall
        limit = top_k * 10 

        # 2. Vector Search (Semantic)
        vector_results = await self._search_vector(query_embedding, limit)
        
        # 3. Keyword Search (Lexical)
        keyword_results = await self._search_keyword(query, limit)

        # 4. Apply RRF
        combined_results = self._apply_rrf(vector_results, keyword_results, k=60)
        
        # 5. Return Top K sorted by RRF score
        # Note: combined_results contains (embedding_obj, score) tuples
        return [item[0] for item in combined_results[:top_k]]

    async def _search_vector(self, query_vector: List[float], limit: int) -> List[Embedding]:
        stmt = select(Embedding).order_by(
            Embedding.embedding.l2_distance(query_vector)
        ).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def _search_keyword(self, query: str, limit: int) -> List[Embedding]:
        # 1. 형태소 분석을 통해 명사 추출
        nouns = extract_nouns(query)
        
        # 2. 명사가 추출된 경우 OR 조건으로 검색 (Recall 향상)
        if nouns:
            conditions = [Embedding.content.ilike(f"%{noun}%") for noun in nouns]
            # 원본 쿼리도 포함 (정확도 보장)
            conditions.append(Embedding.content.ilike(f"%{query}%"))
            
            stmt = select(Embedding).where(
                or_(*conditions)
            ).limit(limit)
        else:
            # 명사가 없으면 기존 단순 포함 검색 (Fallback)
            search_pattern = f"%{query}%"
            stmt = select(Embedding).where(
                Embedding.content.ilike(search_pattern)
            ).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()

    def _apply_rrf(self, vector_results: List[Embedding], keyword_results: List[Embedding], k: int = 60) -> List[tuple]:
        """
        Reciprocal Rank Fusion
        Score = 1 / (k + rank)
        """
        scores = {}
        
        # Rank Vector Results
        for rank, doc in enumerate(vector_results):
            if doc.id not in scores:
                scores[doc.id] = {"doc": doc, "score": 0.0}
            scores[doc.id]["score"] += 1.0 / (k + rank + 1)
            
        # Rank Keyword Results
        for rank, doc in enumerate(keyword_results):
            if doc.id not in scores:
                scores[doc.id] = {"doc": doc, "score": 0.0}
            scores[doc.id]["score"] += 1.0 / (k + rank + 1)
            
        # Sort by combined score descending
        sorted_docs = sorted(scores.values(), key=lambda x: x["score"], reverse=True)
        return [(item["doc"], item["score"]) for item in sorted_docs]