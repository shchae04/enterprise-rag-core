from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.logging import logger

class RerankResult:
    def __init__(self, document_id: str, content: str, score: float, filename: str):
        self.document_id: str = document_id
        self.content: str = content
        self.score: float = score
        self.filename: str = filename

class BaseReranker(ABC):
    """
    Reranker Interface
    나중에 BGE-Reranker, Cohere API 등으로 교체 시 이 클래스를 상속받으면 됩니다.
    """
    @abstractmethod
    async def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[RerankResult]:
        pass

class KeywordReranker(BaseReranker):
    """
    Simple Keyword Boosting Reranker
    벡터 검색(의미 기반)의 약점인 '정확한 단어 매칭'을 보완합니다.
    """
    def __init__(self, boost_weight: float = 0.2):
        self.boost_weight: float = boost_weight

    async def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[RerankResult]:
        logger.info(f"Reranking {len(documents)} documents for query: '{query}'")
        
        # 1. 간단한 토크나이징 (공백 기준)
        # 한국어 형태소 분석기(Kiwi 등)를 붙이면 성능이 더 좋아집니다.
        query_tokens = set(query.split())
        
        reranked_results: List[RerankResult] = []
        
        for doc in documents:
            # ChatService에서 넘어오는 점수는 Similarity Score (Higher is better)
            original_score: float = doc.get('score', 0.0)
            content: str = doc.get('content', "")
            
            # 2. 키워드 매칭 개수 계산
            match_count = 0
            for token in query_tokens:
                if token in content:
                    match_count += 1
            
            # 3. 점수 보정 (점수를 높여줌)
            # 매칭된 키워드 하나당 boost_weight 만큼 점수 추가
            boost_score = match_count * self.boost_weight
            final_score = original_score + boost_score
            
            reranked_results.append(RerankResult(
                document_id=str(doc.get('document_id')),
                content=content,
                score=final_score,
                filename=str(doc.get('filename'))
            ))

        # 4. 점수(Score) 내림차순 정렬 (점수가 높을수록 유사함)
        reranked_results.sort(key=lambda x: x.score, reverse=True)
        
        return reranked_results
