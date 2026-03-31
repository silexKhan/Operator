# 📞 Operator (교환): Universal Protocol Engine 🛡️⚡️

**Operator (교환)**는 조직 전체의 산출물이 일관된 표준(**Protocols**)을 준수하도록 중앙에서 회선을 연결하고 통제하는 **하네스 엔지니어링(Harness Engineering)** 기반의 범용 규약 엔진입니다.

---

## 🚀 Quick Start (초기 구축 및 기동)

어떤 환경에서도 단 한 번의 명령으로 지휘소를 가동할 수 있습니다. 윈도우와 맥을 모두 지원합니다.

### 1. 지휘소 가동 (One-Command)
`web` 폴더로 이동하여 자신의 OS에 맞는 실행 파일을 가동하세요.
- **Mac/Linux:** `cd web && ./start.sh`
- **Windows:** `web/start.bat` (더블 클릭)

> **💡 안내:** 위 명령어를 실행하면 `Node.js` 및 `Python` 환경 점검, 패키지 자동 설치, 웹 서버 기동까지 원스톱으로 진행됩니다. 🛡️⚡️

---

## 🏗️ 1. 핵심 개념 (Core Concepts)

### 📞 Operator & Circuits (교환 및 회선)
- **Operator:** 중앙에서 모든 통신 신호를 중계하고 규약을 강제하는 지휘 주체입니다.
- **Circuit:** 특정 프로젝트나 도메인(예: GDR, MCP)을 의미하며, 독립적으로 격리된 작전 구역입니다.

### 🛡️ Protocols & Harness (규약 및 하네스)
- **Protocols:** AI가 해당 회선에서 반드시 준수해야 할 행동 수칙입니다.
- **Harness Engineering:** 규약을 어기는 행위(수정, 생성 등)를 엔진 레벨에서 물리적으로 차단(Rejection)하여 AI를 정해진 궤도 내로 구속하는 제어 기술입니다.

---

## 📂 2. 시스템 구조 (System Architecture)

```text
.
├── circuits/           # 🏢 회선 등록소 (Circuits Registry)
│   └── registry/
│       └── development/
│           ├── mcp/    # 오퍼레이터 자체 관리 회선
│           └── gdr/    # 골프존 GDR 프로젝트 회선
├── core/               # ⚙️ 교환 엔진 (Operator Heart)
│   ├── harness.py      # 물리적 구속 장치 (Enforcement Unit)
│   ├── protocols.py    # 최상위 공통 규약 (Constitution)
│   └── scanner.py      # 실시간 소스 분석기 (AST Scanner)
├── web/                # 🌐 웹 관제소 (Control Center UI)
└── start.sh / .bat     # 🚀 통합 기동 스크립트
```

---

## 📜 3. 규약 계층 구조 (Protocol Hierarchy)

AI 모델은 업무 수행 시 반드시 아래의 계층적 규약을 상속받아 준수해야 합니다. ⚖️

1.  **Level 0: Global Protocols (`core/protocols.py`)**
    - 전 조직의 절대 원칙 (예: 생략 금지, 보안 최우선).
2.  **Level 2: Circuit Protocols (`circuits/registry/.../protocols.py`)**
    - 개별 프로젝트 전용 수칙 (예: GDR Swift MVVM 표준).

---

## 🤖 4. AI 에이전트 연결 가이드 (MCP Integration)

다른 AI(Claude, ChatGPT 등)가 이 오퍼레이터 지휘소에 연결되려면 아래의 설정을 사용하십시오.

### 🛠️ MCP Server Configuration
`mcp.json` 또는 클라이언트 설정 파일에 아래 내용을 추가합니다. (경로는 실제 위치로 자동 감지됩니다.)

```json
{
  "mcpServers": {
    "operator": {
      "command": "[PROJECT_ROOT]/.venv/bin/python",
      "args": ["[PROJECT_ROOT]/main.py"],
      "env": {
        "PYTHONPATH": "[PROJECT_ROOT]"
      }
    }
  }
}
```
*※ 윈도우의 경우 파이썬 경로는 `.venv/Scripts/python.exe`를 사용하십시오.*

---

## 📡 5. 주요 지휘 도구 (Mission Tools)

- **`get_operator_status`**: 현재 연결된 모든 회선의 상태를 확인합니다.
- **`get_full_json_structure`**: [웹 전용] 전체 프로젝트의 정밀 지도를 JSON으로 추출합니다.
- **`update_circuit_protocols`**: 웹 관제소에서 하달한 명령을 실제 소스에 박아넣습니다. (하네스 작동 🛡️)
- **`browse_directory`**: 서버의 물리적 폴더를 훑어 프로젝트 경로를 조준합니다.

---
**Status:** 📡 Operator (교환) Online | 📞 Circuits Connected | 🛡️ Harness: ARMED
