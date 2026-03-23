# 🌐 Silex MCP Hub: Multi-Platform Setup Guide

이 프로젝트는 **Model Context Protocol (MCP)** 표준을 준수합니다. 
대장님의 모든 AI 에이전트(Claude Desktop, Cursor, Gemini CLI 등)에 이 허브를 연결하여 통합 온톨로지 환경을 구축할 수 있습니다.

---

## 1. 파이썬 환경 구축 (Environment)
프로젝트를 로드하기 위한 파이썬 가상환경을 먼저 세팅합니다.

```bash
# 1. 프로젝트 루트 폴더로 이동
cd workspace/private/MCP

# 2. 가상환경 생성 및 패키지 설치
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. 클라이언트별 연결 설정 (Integration)

각 AI 플랫폼의 설정 파일에 아래의 **표준 JSON 구성**을 추가하세요.
**(주의: 모든 경로는 반드시 본인 컴퓨터의 '절대 경로'로 입력해야 합니다!)**

### 📦 공통 JSON 구성 (Standard Config)
```json
{
  "mcpServers": {
    "silex-hub": {
      "command": "/Users/silex/workspace/private/MCP/.venv/bin/python",
      "args": ["/Users/silex/workspace/private/MCP/main.py"]
    }
  }
}
```

### 🛠️ 플랫폼별 설정 위치
1. **Claude Desktop**
   - 경로: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - 위 JSON 구성을 파일 전체 구조에 맞춰 병합하세요.

2. **Cursor (IDE)**
   - 설정 메뉴: `Settings` -> `Features` -> `MCP`
   - `+ Add Server` 클릭
   - Name: `silex-hub`
   - Type: `command`
   - Command: 위 JSON의 `command`와 `args`를 합쳐서 입력
     (예: `/Users/silex/.../.venv/bin/python /Users/silex/.../main.py`)

3. **Gemini CLI**
   - 경로: `~/.gemini/mcp.json`
   - `mcpServers` 항목 하위에 위 구성을 추가하세요.

---

## 3. 정상 작동 확인 (Validation)
연결된 AI 에이전트에게 다음과 같이 질문하여 허브가 정상 인식되었는지 확인합니다.

> **"Silex 허브의 상태를 확인해줘"** 또는 **"get_hub_status 도구를 실행해줘"**

**성공 시 응답 예시:**
```text
🚀 Hub Status: Online
📍 CWD: /Users/silex/workspace/project/GDR
🏢 Active Tenant: GDR
🛡️ Core Axioms: Active (Dumb-View, SWR, Safety-First)
```

---

## 💡 유지보수 팁
- **절대 경로 사용:** AI 클라이언트는 상대 경로를 인식하지 못하므로 반드시 `/Users/...`로 시작하는 전체 경로를 사용하세요.
- **가상환경 실행:** `command` 필드에 가상환경 내부의 파이썬 경로(`.venv/bin/python`)를 직접 지정하면 별도의 `source activate` 없이도 의존성이 완벽하게 로드됩니다.

---
*Created by Gemini AIP - The Universal Master Architect for Captain Silex.*
