# 🛰️ Operator

**Harness Engineering Framework optimized for Gemini CLI**
*Gemini CLI 환경에 최적화된 대규모 시스템 하네스 및 가버넌스 프레임워크*

[English](#english) | [한국어](#korean)

---

<a name="english"></a>
## 🌍 English

Operator is a system governance framework designed to manage complex harness engineering. It acts as an "extended hand" for **Gemini CLI**, enabling AI to orchestrate large-scale projects while maintaining perfect protocol integrity.

This project is deeply inspired by the movie *The Matrix*. It represents the ongoing journey of building a sophisticated system to command and control "The Machine." We are looking for passionate contributors who want to join this mission and help shape the future of system orchestration. Your participation is more than welcome.

### 🔗 Integration with Gemini CLI
Add the following to your `mcp.json` to link Gemini CLI with the Operator Engine:

```json
{
  "mcpServers": {
    "operator": {
      "command": "python3",
      "args": ["/absolute/path/to/operator/mcp_operator/engine/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/operator"
      }
    }
  }
}
```

### 🔌 Core Concept: Circuits
A **Circuit** is a **policy unit for projects or milestones**. 
- **Setup**: Create a circuit for your project (e.g., `New_App_Launch`) and define its unique protocols.
- **Isolation**: Each project lives in its own circuit, ensuring rules don't get mixed up.
- **Milestone Governance**: Establish strict criteria for specific development phases.

### 🎬 Initial Usage
Once the MCP configuration is complete and Gemini CLI is running, you can command the AI as if you are calling the bridge:
> **"Operator, connect to [circuit_name]"**

The AI will then establish a link to the specified circuit and automatically load all the user-defined protocols and guides into its active context.

### 🛡️ How to use Sentinel (Practical Workflow)
The **Sentinel** is your autonomous auditor. Here is how you actually use it:

1. **Deployment**: In the Hovercraft UI, add the `sentinel` unit to your active circuit.
2. **Commanding the AI**: When giving tasks to Gemini CLI, explicitly instruct it to use Sentinel.
   - *Example*: "Gemini, **use Sentinel** to implement the login logic."
   - *Example*: "Proceed with the UI refactoring **via Sentinel protocol**."
3. **Autonomous Execution**: Once the "Sentinel" command is given, the AI will:
   - Automatically draft a PRD and ADR.
   - Self-audit the code against system equations.
   - Refuse to finish until it achieves a **PASS** status from the Sentinel unit.

### 🚀 Running Hovercraft (Management UI)
Hovercraft is the visual radar for Gemini CLI's actions.
1. Run `./start.sh` to initialize.
2. Access at **`http://localhost:3000`**.

---

<a name="korean"></a>
## 🇰🇷 한국어

오퍼레이터(Operator)는 대규모 프로젝트의 복잡한 하네스 엔지니어링과 협업 규약을 관리하기 위한 프레임워크입니다. 특히 **Gemini CLI**와 결합하여, AI가 시스템의 질서를 유지하며 거대한 코드 베이스를 지휘할 수 있게 합니다.

이 프로젝트는 영화 '매트릭스'에서 깊은 영감을 받았으며, '기계(The Machine)'를 지휘하고 통제하는 시스템을 구축해 나가는 과정입니다. 이 여정에 함께하며 시스템의 질서를 만들어갈 분들의 많은 관심과 참여를 기다립니다.

### 🔗 Gemini CLI 연결 설정
`mcp.json` 파일에 아래 설정을 추가하여 오퍼레이터 엔진을 연결하십시오:

```json
{
  "mcpServers": {
    "operator": {
      "command": "python3",
      "args": ["/절대경로/to/operator/mcp_operator/engine/server.py"],
      "env": {
        "PYTHONPATH": "/절대경로/to/operator"
      }
    }
  }
}
```

### 🔌 핵심 개념: 회선 (Circuits)
**회선(Circuit)**은 단순한 채널이 아닌 **프로젝트 또는 마일스톤 단위의 정책 집합**입니다.
- **설정 (Setup)**: 진행 중인 프로젝트(예: `신규_앱_런칭`) 전용 회선을 만들고 규약을 정의합니다.
- **격리 (Isolation)**: 각 프로젝트는 독립된 회선에서 관리되어 서로의 규칙이 충돌하지 않습니다.
- **마일스톤 거버넌스**: 알파 구현, 보안 감사 등 단계별 성공 기준을 설정합니다.

### 🎬 초기 사용법
MCP 설정이 완료된 후 Gemini CLI를 실행하여 오퍼레이터에게 다음과 같이 명령하십시오:
> **"오퍼레이터, [회선이름] 회선 연결해줘"**

명령을 받으면 AI는 즉시 해당 회선으로 연결을 전환하며, 사용자가 미리 설정해둔 모든 가이드와 규약들을 자신의 컨텍스트에 자동으로 탑재합니다.

### 🛡️ 센티널 실전 사용법 (사용자 워크플로우)
**센티널(Sentinel)**은 사용자의 지시를 받아 AI의 작업을 감시하는 자율 감사관입니다.

1. **유닛 배치**: 호버크래프트 UI에서 관리 중인 회선에 `sentinel` 유닛을 추가합니다.
2. **AI에게 지시**: Gemini CLI에 업무를 시킬 때, 반드시 **"센티널을 사용하라"**고 명시합니다.
   - *명령 예시*: "Gemini, **센티널을 사용해서** 로그인 로직을 구현해줘."
   - *명령 예시*: "**센티널 규약에 따라** UI 리팩토링을 진행해."
3. **자율 작업 프로세스**: "센티널" 명령을 받은 AI는 다음 과정을 스스로 수행합니다:
   - 작업 시작 전 기획서(PRD) 및 설계서(ADR) 자동 작성.
   - 코드를 수정할 때마다 시스템 방정식에 맞는지 실시간 자가 진단.
   - 센티널 유닛으로부터 **PASS** 판정을 받기 전까지는 작업을 종료하지 않고 완벽함을 추구함.

### 🚀 실행 및 모니터링
1. `./start.sh` 명령어로 시스템 가동.
2. 브라우저에서 **`http://localhost:3000`** (Hovercraft UI) 접속.

## 📄 License
**MIT License** - Anyone can modify and distribute for collaboration excellence.

---
*Created by Operator Team for Harness Engineering Excellence via Gemini CLI.*
