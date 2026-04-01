#  Operator (교환): Universal Protocol & Circuit Engine 

**Operator (교환)**는 조직 전체의 산출물이 일관된 표준(**Protocols**)을 준수하도록 중앙에서 회선을 연결하고 통제하는 **하네스 엔지니어링(Harness Engineering)** 기반의 지능형 규약 엔진입니다. AI 모델의 업무 수행 궤도를 정밀하게 관리하고 품질을 보증하는 디지털 지휘소 역할을 수행합니다.

---

##  Quick Start: Genesis Launch 🚀

어떤 환경에서도 단 한 번의 명령으로 지휘소를 가동할 수 있습니다. 윈도우와 맥을 모두 지원합니다.

### 1. 지휘소 가동 (One-Command)
`web` 폴더로 이동하여 자신의 OS에 맞는 실행 파일을 가동하세요.
- **Mac/Linux:** `cd web && ./start.sh`
- **Windows:** `web/start.bat` (더블 클릭)

### 2. 자동화 프로세스 (Hyper-Autonomous)
위 명령어를 실행하면 시스템이 아래 작업들을 자동으로 수행하며 최적의 작전 환경을 구축합니다:
- **환경 점검**: Node.js 및 Python 설치 여부와 버전 정합성 자동 확인.
- **패키지 빌드**: `npm install`을 통한 웹 관제소(Next.js) 의존성 구축.
- **가상환경 격리**: `.venv` 생성 및 `requirements.txt` 기반의 파이썬 라이브러리 동기화.
- **엔진 기동**: Next.js 서버와 백엔드 MCP 브릿지를 즉시 연결.

---

##  1. 핵심 아키텍처 (Core Architecture)

###  Operator & Circuits (교환 및 회선)
- **Operator (Master Unit):** 중앙에서 모든 통신 신호를 중계하고 규약을 강제하는 지휘 주체입니다.
- **Circuit (Domain Unit):** 특정 프로젝트나 도메인을 의미하며, 독립적으로 격리된 작업 환경(Registry)입니다.

###  Protocols & Harness (규약 및 하네스)
- **Protocols (Standard Unit):** AI가 해당 회선에서 반드시 준수해야 할 행동 수칙 및 기술 표준입니다.
- **Harness Engineering:** 규약을 어기는 행위를 엔진 레벨에서 물리적으로 차단(Rejection)하여 AI를 정해진 궤도 내로 구속하는 품질 보증 기술입니다. 모든 지시 사항은 **Sentinel Unit**에 의해 사전 검증됩니다.

---

##  2. 지휘 계통 및 운영 (Command & Control) 🛰️

###  종합 상황실 (Mission Dashboard)
- **접속 주소**: [http://localhost:3000](http://localhost:3000)
- **기능**: 실시간 프로젝트 **의존성 지도(Architecture Map)** 조망, 활성화된 회선 및 기술 유닛의 실시간 상태 모니터링.

###  명령 제정실 (Circuit Command)
- **회선 관리**: 대시보드에서 특정 회선을 클릭하여 진입.
- **OVERVIEW**: 회선의 물리적 경로, 설명, 의존성 및 배속된 기술 유닛을 정밀 제어.
- **ACTIVE PROTOCOLS**: AI 행동 수칙을 타일 버튼 형태로 관리하며, 수정 즉시 물리적 소스 코드에 반영.

---

##  3. 시스템 구조 (System Architecture)

```text
.
├── circuits/           #  회선 등록소 (Circuits Registry)
│   └── registry/
│       ├── development/
│       │   ├── mcp/    # 오퍼레이터 자체 관리 회선
│       │   └── research/ # 전략적 리서치 및 분석 회선
│       └── design/     # 디자인 및 에셋 관리 회선
├── core/               #  교환 엔진 (Operator Heart)
│   ├── actions.py      # 핵심 명령 처리 유닛 (Action Unit)
│   ├── harness.py      # 물리적 구속 장치 (Enforcement Unit)
│   ├── protocols.py    # 최상위 공통 규약 (Constitution)
│   └── scanner.py      # 실시간 소스 분석기 (AST Scanner)
├── units/              #  기술 전문 유닛 (Tech Units)
│   ├── python/         # 파이썬 기술 표준 및 규약
│   └── markdown/       # 문서화 표준 및 규약
├── web/                #  웹 관제소 (Control Center UI)
└── main.py             #  MCP 서버 진입점 (Server Entry)
```

---

##  4. 규약 계층 구조 (Protocol Hierarchy)

AI 모델은 업무 수행 시 반드시 아래의 계층적 규약을 상속받아 준수해야 합니다. 

1.  **Level 0: Global Protocols (`core/protocols.py`)**
    - 전 조직의 절대 원칙 (예: 정보의 완전성, 보안 우선, 선 보고 후 실행).
2.  **Level 1: Unit Protocols (`units/*/protocols.json`)**
    - 특정 기술 스택 전용 수칙 (예: Python PEP 8, Async IO 우선).
3.  **Level 2: Circuit Protocols (`circuits/registry/.../protocols.py`)**
    - 개별 프로젝트 전용 도메인 수칙 (예: 프로젝트 아키텍처 가이드라인).

---

##  5. AI 에이전트 연결 가이드 (MCP Integration)

Claude, Gemini 등 외부 AI가 이 오퍼레이터 지휘소에 연결되려면 아래의 설정을 사용하십시오.

```json
{
  "mcpServers": {
    "operator": {
      "command": "[PROJECT_ROOT]/.venv/bin/python",
      "args": ["[PROJECT_ROOT]/main.py"],
      "env": {
        "PYTHONPATH": "[PROJECT_ROOT]",
        "MCP_ROOT": "[PROJECT_ROOT]"
      }
    }
  }
}
```

---

##  6. 주요 지휘 도구 (Mission Tools)

- **`get_operator_status`**: 시스템 전체 상태 및 등록된 모든 회선 목록 확인.
- **`mcp_operator_get_full_json_structure`**: [웹 전용] 전체 프로젝트의 정밀 지도를 JSON으로 추출.
- **`mcp_operator_browse_directory`**: 서버의 물리적 폴더 탐색 및 정밀 조준.
- **`mcp_operator_get_circuit_protocols`**: 특정 회선의 전용 규약 정보 로드.
- **`sentinel_set_mission`**: 작업의 목적(Objective)과 성공 기준(Criteria) 설정.

---
**Status:**  Operator (교환) Online |  Circuits Connected |  Harness: ARMED
