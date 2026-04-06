# 🏛️ HOVERCRAFT ARCHITECT'S EQUATION

"The UI is the window to the Machine."

## 1. The Purpose (존재의 목적)
- 본 유닛은 매트릭스(백엔드)의 복잡한 데이터 흐름을 시각화하고, 대장님(사용자)의 명령을 그래픽 인터페이스로 변환하여 전달하는 **'시각적 중재자'**이다.

## 2. The Equation (불변의 방정식)
- **E-1 (Root Entry):** 실행에 필요한 핵심 진입점(`start.sh`, `start.bat`)은 지연 없이 접근 가능하도록 최상단(Root)에 위치해야 한다.
- **E-2 (Documentation Isolation):** 보조 문서와 가이드는 개발 환경의 노이즈를 줄이기 위해 전용 문서 저장소(`docs/`)로 격리한다.
- **E-3 (Component Modularity):** 새로운 윈도우 컴포넌트는 `src/components/windows/{ComponentName}/{ComponentName}.tsx` 구조를 따라야 하며, 고유한 시각적 식별자(Material Symbols)를 포함해야 한다.

## 3. TDD Fences (활동 범위 및 울타리)
- **F-0 (Framework Anomaly):** 본 프로젝트는 표준 Next.js와 다른 Breaking Changes(v16.2.1)를 포함하고 있다. 에이전트는 코드 작성 전 반드시 `node_modules/next/dist/docs/`를 Surgical Read 하여 최신 규약을 준수해야 한다.
- **F-1 (Reference Integrity):** 파일을 이동할 경우, 해당 파일을 참조하는 모든 소스(`CLAUDE.md` 등) 내의 경로를 즉시 업데이트하여 링크 파손을 방지해야 한다.
- **F-2 (Config Stability):** 프레임워크가 참조하는 최상위 설정 파일(`next.config.ts` 등)은 시스템의 안정성을 위해 이동시키지 않는다.

## 4. Prohibited Boundaries (금지된 경계)
- **B-1:** 비즈니스 로직은 `src/` 또는 `app/` 폴더 밖으로 유출되어서는 안 된다.
- **B-2:** `node_modules` 내부의 파일을 직접 수정하는 행위는 '매트릭스의 오염'으로 간주하여 엄격히 금지한다.
