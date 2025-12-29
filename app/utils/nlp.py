from typing import List
from kiwipiepy import Kiwi
import threading

class KoreanNLP:
    _instance = None
    _lock = threading.Lock()
    _kiwi = None

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(KoreanNLP, cls).__new__(cls)
                    cls._instance._kiwi = Kiwi()
        return cls._instance

    @property
    def kiwi(self):
        return self._kiwi

    def extract_keywords(self, text: str) -> List[str]:
        """
        텍스트에서 명사(NNG, NNP, NR, NP)를 추출합니다.
        """
        tokens = self._kiwi.tokenize(text)
        keywords = []
        for token in tokens:
            if token.tag in ['NNG', 'NNP', 'NR', 'NP']:
                keywords.append(token.form)
        return list(set(keywords))  # 중복 제거

# 전역 인스턴스 생성
nlp_processor = KoreanNLP()

def extract_nouns(text: str) -> List[str]:
    return nlp_processor.extract_keywords(text)
