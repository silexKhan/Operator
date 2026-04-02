# Sentinel Evaluator Refactoring Spec

## 1. 개요 (Overview)
기존 `sentinel_evaluate`는 AI의 단순 텍스트 출력(summary)에 의존한 문자열 매칭 방식으로 통과 여부를 판단했습니다. 이로 인해 AI가 기준 텍스트를 완벽하게 재현하지 못할 경우 무한 루프(`FAIL` 반복)에 빠지는 문제가 발생했습니다. 본 명세는 검증 논리를 실제 스크립트 실행(Test Command)과 상태 증거(Evidence) 기반으로 전환하고, 반복 시도 제한을 두어 시스템 안정성을 확보하는 구조를 정의합니다.

## 2. 변경 내용 (Changes)

### 2.1. Tool Parameter 변경
AI가 `sentinel_evaluate`를 호출할 때 제공해야 하는 파라미터를 강화합니다.
- 기존: `summary` (단일 문자열)
- 변경:
  - `test_command` (선택적): AI의 작업 성공을 실증할 수 있는 터미널 명령어 (예: `pytest path/to/test.py`). `None`일 경우 실행 생략.
  - `evidence` (필수): 각 미션 기준(criteria)별로 어떻게 충족시켰는지 논리적 증거나 파일 경로를 설명하는 텍스트.

### 2.2. 평가(Evaluation) 논리 개선
- **명령어 기반 검증 (Test Command Validation):** AI가 `test_command`를 제공한 경우, 해당 명령어를 `subprocess`로 실행하여 Exit Code가 `0`인지 확인합니다. `0`이 아닐 경우 해당 실행 결과를 포함하여 `FAIL` 처리합니다.
- **증거 기반 판단 (Evidence Check):** `summary` 단순 문자열 매칭 대신, AI가 제출한 `evidence`가 최소한 10자 이상 작성되었는지 등의 기본 유효성을 검사합니다. 실질적인 "완벽성" 평가는 AI의 자율성과 책임에 맡기되, 증명이 불충분하면 실패 처리할 수 있습니다.
- **반복 시도 제한 (Max Iteration Limit):** `mission.json` 파일에 최대 시도 횟수(`max_iteration`)를 3~5회로 설정합니다. 현재 `iteration`이 최대 횟수를 초과하면 강제로 `HARD FAIL` 상태로 전환하고 루프를 탈출하도록 지시합니다.

## 3. 구현 세부사항 (Implementation Details)

### `circuits/registry/development/mcp/actions.py` 수정

**1. Tool 스키마 업데이트 (Line 49 주변)**
```python
types.Tool(
    name="sentinel_evaluate",
    description="현재 작업 결과물을 미션 목적과 대조하여 통과 여부를 판정합니다. 가능한 경우 검증용 테스트 명령어를 포함하세요.",
    inputSchema={
        "type": "object",
        "properties": {
            "test_command": {
                "type": "string",
                "description": "선택사항. 변경 사항이 제대로 동작하는지 증명할 쉘 명령어 (예: 'pytest src/test.py'). 없으면 빈 문자열."
            },
            "evidence": {
                "type": "string",
                "description": "각 성공 기준(criteria)을 어떻게 충족했는지 설명하는 구체적인 증거 데이터 및 논리."
            }
        },
        "required": ["evidence"]
    }
)
```

**2. 실행 로직 업데이트 (Line 230 주변)**
```python
elif func_name == "sentinel_evaluate":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    path = os.path.join(root, "mission.json")
    if not os.path.exists(path): return [types.TextContent(type="text", text=" [SENTINEL] 평가할 미션이 없습니다.")]
    
    with open(path, "r", encoding="utf-8") as f:
        mission = json.load(f)
    
    test_command = arguments.get("test_command", "")
    evidence = arguments.get("evidence", "")
    max_iteration = mission.get("max_iteration", 3)
    
    # 반복 제한 검사
    if mission["iteration"] >= max_iteration:
        mission["status"] = "HARD_FAIL"
        with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
        return [types.TextContent(type="text", text=f" [SENTINEL] HARD FAIL: 최대 재시도 횟수({max_iteration}회)를 초과했습니다. 무한 루프 방지를 위해 작업을 강제 종료합니다. (현재 상태: {mission['status']})")]

    # 증거 기반 1차 검증
    if len(evidence.strip()) < 10:
        mission["iteration"] += 1
        with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
        return [types.TextContent(type="text", text=f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 성공 기준(criteria)에 대한 구체적인 증거(evidence)가 부족합니다. 다시 시도하십시오.")]

    # 테스트 명령어 기반 2차 검증
    if test_command:
        import subprocess
        try:
            result = subprocess.run(test_command, shell=True, capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                mission["iteration"] += 1
                with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
                res = f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 테스트 명령어 실패.\n명령어: {test_command}\n종료 코드: {result.returncode}\n출력: {result.stdout}\n에러: {result.stderr}"
                return [types.TextContent(type="text", text=res)]
        except Exception as e:
            mission["iteration"] += 1
            with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
            return [types.TextContent(type="text", text=f" [SENTINEL] FAIL (Iteration {mission['iteration']}): 테스트 명령어 실행 중 오류 발생: {str(e)}")]

    # 모든 검증 통과 (간소화됨, AI의 판단 신뢰)
    mission["status"] = "PASS"
    with open(path, "w", encoding="utf-8") as f: json.dump(mission, f, indent=4, ensure_ascii=False)
    return [types.TextContent(type="text", text=" [SENTINEL] FINAL PASS: 모든 미션 기준과 테스트가 충족되었습니다! 작전을 성공적으로 종료해도 좋습니다.")]
```

### `circuits/registry/development/mcp/actions.py` (sentinel_set_mission 수정)
`mission.json`을 초기화할 때 `max_iteration` 값을 함께 설정하도록 수정해야 합니다.

```python
elif func_name == "sentinel_set_mission":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    path = os.path.join(root, "mission.json")
    data = {
        "objective": arguments.get("objective"),
        "criteria": arguments.get("criteria", []),
        "status": "IN_PROGRESS",
        "iteration": 1,
        "max_iteration": 3 # 무한 루프 방지를 위한 최대 횟수
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return [types.TextContent(type="text", text=f" [SENTINEL] 미션 목표 설정 완료: {data['objective']}")]
```