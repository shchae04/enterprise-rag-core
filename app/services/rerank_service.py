from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.core.logging import logger

class RerankResult:
    def __init__(self, document_id: str, content: str, score: float, filename: str):
        self.document_id = document_id
        self.content = content
        self.score = score
        self.filename = filename

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
        self.boost_weight = boost_weight

    async def rerank(self, query: str, documents: List[Dict[str, Any]]) -> List[RerankResult]:
        logger.info(f"Reranking {len(documents)} documents for query: '{query}'")
        
        # 1. 간단한 토크나이징 (공백 기준)
        # 한국어 형태소 분석기(Mecab 등)를 붙이면 성능이 더 좋아집니다.
        query_tokens = set(query.split())
        
        reranked_results = []
        
        for doc in documents:
            # 원본 벡터 유사도 점수 (L2 거리이므로 작을수록 좋음 -> 역수로 변환하거나 정규화 필요)
            # 여기서는 편의상 L2 Distance를 그대로 사용하되, 로직을 '점수' 기반으로 통일하기 위해
            # (1 / (1 + distance)) 방식을 사용하거나, 단순히 거리 값에 페널티를 주는 방식을 쓸 수 있습니다.
            # 하지만 KeywordReranker는 '보너스 점수' 개념이므로, 
            # 기존 순위를 유지하되 키워드가 있으면 '거리'를 줄여주는(더 가깝게 만드는) 방식을 택하겠습니다.
            
            original_distance = doc['score'] # L2 Distance (lower is better)
            content = doc['content']
            
            # 2. 키워드 매칭 개수 계산
            match_count = 0
            for token in query_tokens:
                if token in content:
                    match_count += 1
            
            # 3. 점수 보정 (거리를 줄여줌)
            # 매칭된 키워드 하나당 거리 값을 boost_weight 비율만큼 감소
            # 예: 거리 0.8, 키워드 2개 매칭(0.4 감소) -> 보정 거리 0.4 (상위 랭크로 이동)
            boost_score = match_count * self.boost_weight
            final_score = max(0.0, original_distance - boost_score)
            
            reranked_results.append(RerankResult(
                document_id=doc['document_id'],
                content=content,
                score=final_score,
                filename=doc['filename']
            ))

        # 4. 점수(Distance) 오름차순 정렬 (거리가 짧을수록 유사함)
        reranked_results.sort(key=lambda x: x.score)
        
        return reranked_results
