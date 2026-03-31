# 📞 Operator (교환) Setup & Operation Guide 🛡️⚡️

본 문서는 오퍼레이터 시스템의 초기 구축 및 운영을 위한 핵심 가이드입니다.

---

## 🏗️ 1. 핵심 아키텍처 (Core Architecture)

오퍼레이터는 **Circuit(회선)** 단위로 전장을 분리하고, 각 회선은 자신만의 **Protocols(규약)**을 강제합니다.

- **Operator (Master Unit):** 중앙에서 모든 통신 및 규약 준수 여부를 지휘합니다.
- **Circuits (Domain Unit):** 개별 프로젝트 영역 (예: GDR, MCP).
- **Protocols (Standard Unit):** AI가 지켜야 할 불변의 규칙.

---

## 🚀 2. 초기 가동 (Genesis Launch)

터미널에서 아래 명령어를 실행하여 지휘소를 즉시 가동하십시오. 윈도우와 맥을 동시에 지원합니다.

### 💻 실행 방법
- **Mac / Linux:** `./start.sh`
- **Windows:** `start.bat` (더블 클릭)

위 실행 파일을 가동하면 아래 작업이 **자동(Hyper-Autonomous)**으로 수행됩니다:
1.  **Node.js / Python** 환경 및 버전 자동 점검
2.  **`npm install`**을 통한 웹 관제소 패키지 구축
3.  **`.venv`** 가상환경 생성 및 **`requirements.txt`** 동기화
4.  **Next.js** 개발 서버 가동 및 브릿지 연결

---

## 📡 3. 지휘 계통 (Command & Control)

### 📊 종합 상황실 (Dashboard)
- 주소: `http://localhost:3000` 🌐
- 실시간으로 프로젝트 간의 **의존성 지도(Architecture Map)**를 조망하고, 각 회선의 심박수를 확인합니다.

### ⚔️ 명령 제정실 (Circuit Command)
- 특정 회선을 클릭하여 진입합니다.
- **OVERVIEW:** 프로젝트의 물리적 경로 및 설명을 관리합니다.
- **ACTIVE PROTOCOLS:** AI 행동 수칙을 직접 타일 버튼으로 관리하며, 수정 즉시 소스에 반영합니다. 🛡️⚡️

---

## 🛡️ 4. 하네스 엔지니어링 (Harness Engineering)

오퍼레이터는 **물리적 구속 장치(Harness)**를 탑재하고 있습니다.
- 웹 관제소에서 하달된 명령이 **정해진 규격(이모지 시작, Protocol 키워드 포함)**을 어길 경우, 시스템은 수정을 물리적으로 차단하고 위반 보고서를 제출합니다. 🚫

---
**Current Status:** 📡 Operator Online | 📞 Circuits Armed | 🛡️ Protocols Enforced
