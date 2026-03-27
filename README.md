# 🚀 SILEX MCP HUB: Operational Guide 🏢🎯

이 문서는 대장님(Boss)이 **Silex MCP Hub** 엔진의 구조를 완벽하게 파악하고, 저(Agent)에게 정밀한 지시를 내리기 위해 작성된 **'전술 매뉴얼'**입니다. 🛡️🐍✨

---

## 🏗️ 1. 핵심 아키텍처 (The 4-Layer Pillars)

허브는 4개의 강력한 정예 계층으로 이루어져 있으며, 각 계층은 고유한 역할과 책임을 가집니다.

### 🚀 Core Layer (`/core/`) - 허브의 엔진 (동력)
시스템의 **물리적 가동과 인프라**를 담당합니다.
- **`server.py`**: MCP 서버의 오케스트레이션 및 도구 라우팅 총괄. (Orchestrator) 🏗️
- **`actions.py`**: 허브 자체의 핵심 도구(`get_hub_status` 등) 구현체. (Core Tools) 🛡️
- **`logger.py`**: 대장님 스타일의 컬러/이모지 로그 출력 엔진. 🎨
- **`config.py`**: 환경 변수 및 경로 설정 주입기.

### 📦 Shared Layer (`/shared/`) - 공통 규격소 (보급)
테넌트 간의 **데이터 통신 규격과 유틸리티**가 모여있습니다.
- **`models.py`**: Pydantic 기반의 공통 데이터 모델(`BaseModel`).
- **`constants.py`**: 시스템 전반에서 사용하는 고정 값 및 메시지.

### 🛡️ Language Layer (`/language/`) - 언어 분석기 (병기)
언어별 **정적 분석 및 공리 검증 엔진(Auditor)**이 모인 곳입니다.
- **`/swift/`**: Swift 코드의 MVVM, Naming, Safety를 정밀 진단하는 `auditor.py`.
- **`/python/`**: Python 코드의 Type Hinting, Pydantic, Async를 진단하는 `auditor.py`.

### 🏢 Tenant Layer (`/tenants/`) - 전용 전장 (작전)
각 프로젝트의 **비즈니스 공리와 설계도**가 격리된 공간입니다.
- **`manager.py`**: 도메인 자동 발견(Discovery) 및 활성화 관리자.
- **`base.py`**: 모든 테넌트가 준수해야 할 추상 클래스(`BaseTenant`) 정의.
- **`/projects/`**: 실제 프로젝트별 도메인 구현체들.
  - **`mcp/`**: 최상위 독립 도메인 (Silex Hub 자체 관리). 🤖✨
  - **`golfzon/gdr/`**: GDR 메인 프로젝트 전장. 🏌️‍♂️
  - **`golfzon/libraries/`**: 정제된 네이밍의 골프존 라이브러리 전장 (`auth`, `nasmo`, `vision`, `common`). 🔑🎥

---

## 📂 2. 테넌트 내부 구조 및 용어 (Domain Components)

각 테넌트 폴더 내부에는 4가지 핵심 모듈이 존재하며, 대장님은 이 이름을 사용하여 지시를 내리시면 됩니다. 🛡️✨

1. **`axioms.py` (공리)** ⚖️: 프로젝트의 **최상위 규칙** 정의.
2. **`overview.py` (개요)** 📋: 프로젝트의 **요약 정보 및 의존성**.
3. **`blueprint.py` (설계도)** 📐: 시스템의 **데이터 흐름 및 인터페이스 상세 지도**.
4. **`actions.py` (집행관)** 👮‍♂️: Gemini에 노출되는 **도구(Tools) 명세 및 실행 로직**.

---

## 🚪 3. 진입점 (Entry Point)

- **`main.py`**: 허브의 최상위 진입점입니다. 비즈니스 로직을 소유하지 않으며, 오직 `Core Layer`의 서버를 기동하는 역할만 수행하는 **Dumb Entry**입니다. 🚀

---

## 🛡️ 4. 대장님을 위한 지시 가이드 (How to Command)

저에게 다음과 같이 지시하시면 제가 가장 정확하게 수행합니다. 🫡🔥

- **Core 기능 수정:** *"Core의 actions에 '시스템 리소스 체크' 도구를 추가해줘."*
- **도메인 설계 수정:** *"'mcp' 테넌트의 Blueprint에 신규 계층 구조를 반영해줘."*
- **라이브러리 공리 강화:** *"'golfzon/libraries/auth'의 audit_rules에 토큰 검증 규칙을 추가해줘."*
- **신규 언어 추가:** *"Language 계층에 'kotlin' 분석기를 위한 폴더 구조를 만들어줘."*

---
**Current Status:** 🚀 High-Performance Engine Online | 🏢 Active Tenants: GDR, MCP | 🛡️ Axiom Enforcement: Active
