# 🐍 PYTHON_ARCHITECT: The AST Observer

## 🧩 The Equation (코드 방정식)
**Python Source ➔ [AST Parser] ➔ [ASTAuditor: Visitor Pattern] = Violation List**

- 파이썬 코드는 텍스트가 아닌 '트리(Tree)' 구조로 이해되어야 한다.
- `ASTAuditor`는 노드를 순회하며 정적 무결성을 파괴하는 요소를 색출한다.

## 🛡️ TDD Fence (TDD 울타리)
1. **[P-1] Strict Type Hinting:** 모든 함수의 인자와 반환 타입이 명시되었는가?
2. **[P-2] Pydantic Usage:** 데이터 모델은 `BaseModel`을 상속받았는가?
3. **[P-3] Async IO:** 코어 로직은 비동기(`async/await`)로 작성되었는가?
4. **[P-4] Clean Naming:** 'vc', 'nav' 등 모호한 축약어를 배제했는가?
5. **[S-1] Security Guard:** `eval`, `exec`, `os.system` 호출이 금지되었는가?

## 🏛️ Matrix Design Note
코드는 실행되기 전에 이미 논리적으로 완벽해야 합니다. AST는 거짓말을 하지 않습니다.
