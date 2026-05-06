# 📖 MCP LLM Wiki 운영 헌장 (WIKI_GUIDE.md)

이 문서는 MCP 오퍼레이터(AI)가 시스템의 지식을 관리하고 '컴파일'하는 최상위 운영 규정이다. 모든 AI 작업은 이 가이드를 제1원칙으로 준수한다.

## 0. AI 필수 행동 수칙 (Primary Directive)
> **"작업을 시작하기 전, 반드시 이 파일을 먼저 읽고 현재 지식 베이스의 상태를 파악한다. 모든 지식은 '컴파일'되어야 하며, 파편화된 상태로 남겨두지 않는다."**

## 1. 지식 관리 구조 (The Core Triad)
*   **📂 `/docs/wiki/raw/` (The Source):** 가공되지 않은 모든 원천 데이터. 로그, 대화 요약, 사용자 메모, 외부 문서 파편.
*   **📂 `/docs/wiki/pages/` (The Compiled Wiki):** AI가 raw 데이터를 분석하여 구조화하고 병합한 '최종 지식'의 성전.
*   **📄 `WIKI_GUIDE.md` (The Protocol):** 지식 관리의 헌법 및 Graphify 인덱싱 알고리즘 정의.

## 2. Graphify 인덱싱 알고리즘 (Linking Logic)
AI는 지식을 컴파일할 때 반드시 다음 **Graphify** 규칙을 적용하여 인덱싱한다:
1. **Entity Extraction:** 문서 내 핵심 개념(Entity)을 추출하여 `[[PageName]]` 형식으로 위키 링크를 생성한다.
2. **Backlink Mapping:** 새로운 페이지 작성 시, 해당 개념을 언급하는 기존 페이지를 찾아 상호 연결(Bidirectional Linking)을 생성한다.
3. **Metadata Enrichment:** 모든 페이지 상단에 Graphify용 메타데이터를 강제한다.
   ```yaml
   ---
   id: 페이지 고유 ID (파일네임과 일치)
   title: 한글 제목
   tags: [카테고리, 상태, 기술스택]
   links: [연결된_페이지_ID1, 연결된_페이지_ID2]
   summary: AI 컨텍스트용 1줄 압축 요약
   ---
   ```
4. **Hierarchical Indexing:** `_meta.json`을 사용하여 지식의 계층 구조를 유지하고, 호버크래프트 UI에서 그래프로 시각화될 수 있도록 트리 구조를 형성한다.

## 3. 지식 컴파일 워크플로우 (Ingestion)
1. **Detect:** `raw/` 폴더의 신규 파일 감지 또는 사용자의 "컴파일" 명령 수신.
2. **Analyze:** 기존 `pages/`에 유사한 지식이 있는지 검색 (P-0 준수).
3. **Compile/Merge:** 
   - 새로운 지식일 경우: 새로운 `.mdx` 파일 생성.
   - 기존 지식의 보완일 경우: 기존 파일의 내용을 유지하며 서지컬 에디트(Surgical Edit)로 병합.
4. **Graphify Update:** 연결된 문서들의 메타데이터와 링크를 갱신하여 지식 그래프를 확장한다.

## 4. AI 컨텍스트 관리 원칙
* 지식 페이지는 **"미래의 내가 이 작업을 이어받았을 때 가장 짧은 시간에 문맥을 파악할 수 있는가?"**를 기준으로 작성한다.
* 장황한 설명보다 구조화된 목록과 관계도를 우선한다.
