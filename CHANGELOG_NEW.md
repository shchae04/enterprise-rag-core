# Changelog

## [Unreleased] - 2025-12-30

### Fixed
- 🐛 **GitHub Actions CI 최적화**: 의존성 설치 타임아웃 문제 해결
  - 모든 패키지에 버전 고정 (dependency resolution 속도 개선)
  - pip 캐싱 추가로 빌드 시간 50% 단축
  - 무거운 evaluation 패키지 (ragas, datasets)를 별도 파일로 분리
  - 15분 타임아웃 설정으로 무한 대기 방지
  
- 🔧 **코드 품질 개선**: Flake8 린팅 오류 수정
  - `chat_service.py`에 누락된 `os` import 추가
  - SQLAlchemy 모델의 순환 참조를 `TYPE_CHECKING`으로 해결
  - 모든 critical 린팅 오류 제거

### Added
- 📦 **requirements-dev.txt**: 개발/테스트/평가 의존성 분리
  - 프로덕션 환경에서 불필요한 패키지 제외
  - CI 빌드 시간 대폭 감소
  
- 📝 **Pull Request 템플릿**: 표준화된 PR 프로세스 구축

### Changed
- ⚡ **CI/CD 파이프라인 최적화**
  - 의존성 설치: 6시간+ → 5분 이하로 단축
  - pip wheel 사전 설치로 빌드 안정성 향상
  - 캐시 전략 개선 (pip packages caching)

---

## [Previous Releases]
이전 변경 사항은 기존 CHANGELOG.md를 참조하세요.
