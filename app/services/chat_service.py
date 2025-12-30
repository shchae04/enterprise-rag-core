import os
from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.embedding import Embedding
from app.models.document import Document
from app.services.vector_service import VectorService
from app.services.rerank_service import KeywordReranker
from app.core.config import settings
from app.core.logging import logger
import google.generativeai as genai

class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vector_service = VectorService(db) # Inject VectorService
        # 추후 설정값에 따라 CohereReranker 등으로 교체 가능
        self.reranker = KeywordReranker(boost_weight=0.3) 

    async def get_answer(self, query: str, k: int = 4) -> Tuple[str, List[dict]]:
        # 0. Query Expansion (어휘 불일치 해결)
        expanded_query = await self._expand_query(query)

        # 1. Hybrid Search (Vector + Keyword -> RRF)
        # 이제 VectorService.search_hybrid가 RRF된 상위 문서를 반환합니다.
        # 내부적으로 k * 4개를 후보로 뽑아서 RRF 후 상위 k * 2개 정도를 리턴받는 것이 좋으나,
        # search_hybrid 인터페이스가 top_k를 받으므로, 재순위화를 위해 넉넉히 k * 3개를 요청합니다.
        rrf_limit = k * 3
        
        # Note: search_hybrid returns List[Embedding] (entity objects)
        # We need to fetch associated Document metadata.
        # Ideally search_hybrid should return tuples or we lazy load.
        # But Embedding has document relationship (lazy loading in async might be tricky without specific loader options).
        # Let's verify search_hybrid implementation. It returns Embedding scalars.
        # Accessing embedding.document might trigger lazy load error in async unless we use joinedload or explicit join.
        
        # For performance and correctness, let's modify how we call or use the results.
        # Actually, VectorService methods just execute simple selects.
        # We might need to fetch Document info.
        
        # Let's assume Embedding object has what we need or we fetch documents by ID.
        candidate_embeddings = await self.vector_service.search_hybrid(expanded_query, top_k=rrf_limit)
        
        if not candidate_embeddings:
            return "관련된 문서를 찾을 수 없습니다.", []

        # Fetch Documents for candidates
        # To avoid N+1, let's fetch documents in batch
        doc_ids = list(set([e.document_id for e in candidate_embeddings]))
        stmt = select(Document).where(Document.id.in_(doc_ids))
        result = await self.db.execute(stmt)
        documents_map = {doc.id: doc for doc in result.scalars().all()}

        # 3. Prepare for Final Reranking (Cross-Check or Keyword Boosting again)
        # Hybrid Search already did RRF (which includes keyword match).
        # But our KeywordReranker (in rerank_service.py) might do specific scoring or we can skip it?
        # Hybrid Search (RRF) IS a form of reranking.
        # If we trust RRF, we can just take top K.
        # However, ChatService architecture uses KeywordReranker which might use different logic (e.g. precise exact match boosting).
        # Let's keep it for fine-tuning.
        
        candidate_input = []
        # Since RRF score is not directly attached to embedding object in the return list (it just returns list),
        # we lose the score information unless we modify search_hybrid to return scores.
        # Current search_hybrid returns list of Embeddings.
        # Let's assume order is importance.
        # We can assign mock score based on rank.
        
        for rank, embedding in enumerate(candidate_embeddings):
            doc = documents_map.get(embedding.document_id)
            if not doc: continue
            
            # Reverse rank score (higher is better)
            mock_score = 1.0 / (rank + 1)
            
            candidate_input.append({
                "document_id": str(doc.id),
                "content": embedding.content,
                "score": mock_score,
                "filename": doc.filename
            })

        # 4. Final Reranking (Optional but good for robustness)
        # Using the original query for reranking to focus on user intent (not expanded one)
        # or use expanded? Usually original is better for precision.
        reranked_results = await self.reranker.rerank(query, candidate_input)
        
        # 5. Top-K Slice
        final_top_k = reranked_results[:k]

        # 6. Construct Context
        context_texts = []
        sources = []
        for res in final_top_k:
            context_texts.append(res.content)
            sources.append({
                "document_id": res.document_id,
                "filename": res.filename,
                "content": res.content[:200] + "...",
                "score": res.score
            })

        context = "\n\n".join(context_texts)

        # 7. Generate Answer using LLM
        answer = await self._generate_llm_response(query, context)
        
        return answer, sources

    async def _expand_query(self, query: str) -> str:
        """
        사용자 질문을 확장하여 동의어/유사어를 포함시킵니다.
        """
        try:
            model = genai.GenerativeModel(settings.LLM_MODEL)
            prompt = f"""
당신은 검색 쿼리 확장 전문가입니다.
사용자의 질문을 분석하고, 같은 의미를 가진 유사어, 동의어, 관련 용어를 포함하여 확장된 검색 쿼리를 생성하세요.
단, 원본 질문의 의도를 벗어나지 않도록 주의하세요.

사용자 질문: {query}
확장된 쿼리 (콤마로 구분):
"""
            response = await model.generate_content_async(prompt)
            expanded = response.text.strip()
            logger.info(f"🔍 Query Expansion: '{query}' → '{expanded}'")
            return expanded
        except Exception as e:
            logger.warning(f"⚠️ Query expansion failed, using original query: {e}")
            return query  # 실패 시 원본 쿼리 반환

    async def _generate_llm_response(self, query: str, context: str) -> str:
        try:
            prompt = f"""
            당신은 기업 내부 문서 기반의 AI 어시스턴트입니다.
            아래 제공된 [문서 내용]만을 바탕으로 사용자의 [질문]에 답변하세요.
            문서에 없는 내용은 지어내지 말고 "문서에서 정보를 찾을 수 없습니다"라고 말하세요.

            [문서 내용]
            {context}

            [질문]
            {query}
            
            답변:
            """

            if settings.LLM_PROVIDER == "gemini":
                model = genai.GenerativeModel(settings.LLM_MODEL)
                response = await model.generate_content_async(prompt)
                return response.text
                
            elif settings.LLM_PROVIDER == "openai":
                from openai import AsyncOpenAI
                client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                response = await client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.choices[0].message.content

            elif settings.LLM_PROVIDER == "anthropic":
                from anthropic import AsyncAnthropic
                client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                response = await client.messages.create(
                    model=settings.LLM_MODEL,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            else:
                return f"지원하지 않는 LLM Provider입니다: {settings.LLM_PROVIDER}"

        except Exception as e:
            logger.error(f"Error generating answer: {e}", exc_info=True)
            return "답변 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."