# 🛰️ Operator (교환): Universal Protocol & Circuit Engine 

**Operator (교환)**는 AI 에이전트가 조직의 표준 규약(**Protocols**)을 준수하며 정해진 궤도 내에서 임무를 수행하도록 통제하는 **하네스 엔지니어링(Harness Engineering)** 기반의 지능형 지휘소입니다. 

---

## 🛠️ Installation & Setup (설치 및 설정)

이 시스템은 Python 기반의 백엔드(MCP 서버)와 Next.js 기반의 프론트엔드(관제 UI)로 구성됩니다.

### 1. 사전 요구사항 (Prerequisites)
- **Python**: 3.10 이상 (3.11 권장)
- **Node.js**: 18.0 이상 (LTS 권장)
- **Git**: 소스 관리 및 분석용

### 2. 설치 단계 (Manual Installation)
시스템을 수동으로 구성하려면 다음 명령어를 실행하십시오.

```bash
# 1. 가상환경 생성 및 백엔드 의존성 설치
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. 웹 관제소 의존성 설치
cd hovercraft
npm install
cd ..
```

### 3. 간편 가동 (One-Command Launch)
운영체제에 맞는 실행 스크립트를 사용하여 모든 환경 구축과 서버 기동을 한 번에 처리할 수 있습니다.
- **Mac/Linux**: `./hovercraft/start.sh`
- **Windows**: `hovercraft\start.bat` (관리자 권한 권장)

---

## 🤖 AI 에이전트 연동 가이드 (AI Integration)

이 MCP는 단순한 도구 모음이 아니라, AI의 행동을 교정하고 품질을 보증하는 **지휘 체계**입니다. 에이전트(Claude, Gemini 등)는 아래 지침을 따라야 합니다.

### 1. MCP 서버 등록 (Config)
에이전트 설정 파일에 아래 구성을 추가하여 연결하십시오.

```json
{
  "mcpServers": {
    "operator": {
      "command": "/usr/local/bin/python3", // 실제 .venv 내 python 경로 권장
      "args": ["/path/to/MCP/mcp_operator/main.py"],
      "env": {
        "PYTHONPATH": "/path/to/MCP",
        "MCP_ROOT": "/path/to/MCP"
      }
    }
  }
}
```

### 2. 표준 작전 절차 (Standard Operating Procedure)
에이전트는 업무 시작 시 반드시 다음 단계를 거쳐야 합니다.
1.  **상태 점검**: `get_operator_status`를 호출하여 현재 활성화된 회선과 가용 유닛을 확인합니다.
2.  **회선 전환**: 수행할 임무(예: GDR 코드 수정, 전략 리서치)에 맞는 회선으로 `set_active_circuit(name="...")`을 통해 전환합니다.
3.  **규약 로드**: `mcp_operator_get_circuit_protocols`로 해당 도메인의 행동 지침을 숙지합니다.
4.  **미션 정의**: `sentinel_set_mission`을 통해 달성하고자 하는 목표와 성공 기준을 명시하여 시스템의 감시를 활성화합니다.

### 3. 하네스 엔지니어링 (Harness Engineering)
모든 도구(Tools) 호출은 백엔드의 **Sentinel Unit**에 의해 실시간으로 감시됩니다. 규약에 어긋나는 코드 생성이나 위험한 시스템 명령은 엔진 레벨에서 즉시 차단(Rejection)되며, AI는 차단 사유를 분석하여 행동을 교정해야 합니다.

---

## 🏗️ 시스템 아키텍처 (System Architecture)

```text
.
├── mcp_operator/       #  백엔드 핵심 (Operator Engine)
│   ├── engine/         #  교환 엔진 (Server, Actions, Sentinel)
│   └── registry/       #  도메인 등록소 (Circuits & Units)
│       ├── circuits/   #  회선 로직 (Domain Workflows)
│       └── units/      #  전문 도구 (Tech Auditors)
├── hovercraft/         #  프론트엔드 (Visual Dashboard)
├── data/               #  영속성 레이어 (States & Logs)
└── scripts/            #  운영 자동화 스크립트
```

---

## 🛰️ 주요 지휘 도구 (Core Mission Tools)

- **`get_operator_status`**: 시스템 가동 상태 및 회선 목록 조망.
- **`mcp_operator_get_blueprint`**: 도메인별 설계도 및 의존성 맵 로드.
- **`mcp_operator_mcp_operator_audit_rules`**: 소스 코드가 현재 규약을 준수하는지 정밀 진단.
- **`sentinel_evaluate`**: 수행된 작업이 설정된 미션 기준을 충족하는지 최종 평가.

---
**Status:**  Operator (교환) Online |  Circuits Connected |  Harness: ARMED
