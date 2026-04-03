# 🛰️ Operator (교환): Hovercraft Command Station

> **"Welcome to the Real World."**
> 
> 인류와 기계의 전쟁이 끝나고 시작된 공생의 시대. 오퍼레이터(Operator)는 호버크래프트를 타고 가상 세계의 거대한 데이터 스트림을 항해하며, AI라는 강력한 기계 지능을 제어하여 디지털 생태계를 재건합니다.

---

## 🌌 Project Concept: The Hovercraft Paradigm

이 시스템은 단순한 코딩 도구가 아닌, 매트릭스 세계관의 **호버크래프트 지휘소**를 모델링합니다. 

- **Hovercraft (호버크래프트)**: 오퍼레이터가 탑승하는 최첨단 디지털 함선(UI)입니다. 암흑 속에 가려진 데이터를 조망하고 AI 에이전트에게 명령을 내리는 인터페이스입니다.
- **Operator System (교환 시스템)**: 인간의 의도와 기계의 실행을 연결하는 중앙 허브입니다. 모든 데이터 패킷은 오퍼레이터의 승인과 규약(Protocols)을 거쳐야만 현실 세계에 반영됩니다.
- **Circuits (회선)**: 특정 디지털 작업 구역으로 연결되는 통신 채널입니다. (예: GDR 회선, 전략 리서치 회선 등)
- **Sentinel Unit (센티널 유닛)**: AI의 업무 수행을 실시간으로 감시하고 궤도를 수정하는 **자율주행용 블랙박스 및 항법 장치**입니다.

---

## 🤖 Sentinel Autopilot (센티널 자율 지휘)

우리는 규약을 강제로 묶어두는 '하네스'를 넘어, AI가 스스로 안전하게 비행할 수 있도록 가이드하는 **자율주행(Autopilot)** 시스템을 지향합니다.

- **Real-time Navigation**: AI가 코드를 생성하거나 명령을 내릴 때, 센티널 유닛이 실시간으로 규약 위반 여부를 스캔하여 최적의 경로로 유도합니다.
- **Autonomous Correction**: 위험한 경로(보안 위협, 규약 위반)로 진입 시 시스템이 즉시 개입하여 안전한 궤도로 행동을 교정합니다.
- **Mission Evaluation**: 자율주행이 끝난 후, 센티널은 설정된 미션 목표와 결과물을 대조하여 최종 성공 여부를 판정합니다.

---

## 🛠️ Installation & Setup (설치 및 설정)

### 1. 사전 요구사항 (Prerequisites)
- **Python**: 3.10 이상 (엔진 구동용)
- **Node.js**: 18.0 이상 (호버크래프트 UI 구동용)
- **Git**: 소스 분석 및 형상 관리용

### 2. 가동 절차 (Launch Sequence)
호버크래프트에 전원을 공급하고 지휘소를 활성화하십시오.

```bash
# 1. 의존성 설치 및 환경 구축
cd hovercraft
npm run setup

# 2. 시스템 기동
./start.sh  # Windows: start.bat
```

---

## 📜 Protocol Hierarchy (규약 계층 구조)

AI 모델은 업무 수행 시 반드시 아래의 계층적 규약을 상속받아 준수해야 합니다. 이는 메인프레임에 접속하기 위한 필수 보안 승인 단계입니다.

1.  **Level 0: Global Protocols (`mcp_operator/engine/protocols.py`)**
    - 전 조직의 절대 원칙 (예: 정보의 완전성, 보안 우선, 선 보고 후 실행).
2.  **Level 1: Unit Protocols (`registry/units/*/protocols.json`)**
    - 특정 기술 스택 전용 수칙 (예: Python PEP 8, Swift MVVM Convention).
3.  **Level 2: Circuit Protocols (`registry/circuits/registry/.../protocols.py`)**
    - 개별 프로젝트 전용 도메인 수칙 (예: 프로젝트 아키텍처 가이드라인).

---

## 🤖 AI 에이전트 연동 가이드 (AI Integration)

### 1. MCP 서버 등록 (Config)
에이전트 설정 파일에 아래 구성을 추가하여 연결하십시오.

```json
{
  "mcpServers": {
    "operator": {
      "command": "/usr/local/bin/python3",
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
1.  **Status Scan**: `get_operator_status`로 현재 가용한 회선과 시스템 안정성을 확인합니다.
2.  **Circuit Link**: 수행할 임무에 맞는 회선으로 접속합니다. `set_active_circuit(name="...")`.
3.  **Protocol Sync**: `mcp_operator_get_circuit_protocols`를 통해 해당 회선에서 준수해야 할 금기사항을 동기화합니다.
4.  **Mission Briefing**: `sentinel_set_mission`으로 목표를 정의하여 **Sentinel Autopilot**을 활성화합니다.

---

## 🛰️ 주요 지휘 도구 (Core Mission Tools)

- **`get_operator_status`**: 시스템 가동 상태 및 회선 목록 조망.
- **`mcp_operator_get_blueprint`**: 도메인별 설계도 및 의존성 맵 로드.
- **`mcp_operator_mcp_operator_audit_rules`**: 소스 코드가 현재 규약을 준수하는지 정밀 진단.
- **`sentinel_evaluate`**: 수행된 작업이 설정된 미션 기준을 충족하는지 최종 평가.
- **`mcp_operator_research_analyze_topic`**: 전략적 리서치 회선에서 특정 주제에 대한 심층 분석 수행.

---

## 🏗️ 시스템 아키텍처 (Architecture Map)

```text
/MCP (Command Root)
├── mcp_operator/               #  Operator Heart (지휘 엔진)
│   ├── engine/                 #  Sentinel Autopilot (자율 지휘 로직)
│   └── registry/               #  Circuits & Units Registry (자산 등록소)
├── hovercraft/                 #  Tactical UI (비주얼 지휘소)
├── data/                       #  Persistence (로그 및 상태)
└── scripts/                    #  Automation (운영 도구)
```

---
**Current Status:**  Hovercraft Online |  AI Uplink: STABLE |  **Sentinel: ACTIVE (Autopilot Mode)**
