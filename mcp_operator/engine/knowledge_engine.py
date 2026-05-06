import os
import re
import yaml
from typing import List, Dict, Any

class KnowledgeEngine:
    """
    Graphify 엔진: 마크다운 위키에서 지식 그래프 데이터를 추출하고 관리함.
    """
    def __init__(self, wiki_path: str = "docs/wiki/pages"):
        self.wiki_path = wiki_path
        self.nodes = []
        self.links = []

    def scan_wiki(self) -> Dict[str, Any]:
        """
        위키 페이지를 스캔하여 노드와 엣지(링크) 정보를 생성함.
        """
        self.nodes = []
        self.links = []
        
        if not os.path.exists(self.wiki_path):
            return {"nodes": [], "links": []}

        for filename in os.listdir(self.wiki_path):
            if filename.endswith(".mdx") or filename.endswith(".md"):
                file_path = os.path.join(self.wiki_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    self._parse_page(filename, content)

        return {"nodes": self.nodes, "links": self.links}

    def _parse_page(self, filename: str, content: str):
        """
        개별 페이지의 메타데이터와 본문 내 링크를 파싱함.
        """
        page_id = filename.replace(".mdx", "").replace(".md", "")
        
        # 1. YAML Frontmatter 추출
        frontmatter = {}
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if fm_match:
            try:
                frontmatter = yaml.safe_load(fm_match.group(1))
            except yaml.YAMLError:
                pass

        # 2. 노드 추가
        node = {
            "id": page_id,
            "title": frontmatter.get("title", page_id),
            "tags": frontmatter.get("tags", []),
            "summary": frontmatter.get("summary", ""),
            "updated": frontmatter.get("updated", "")
        }
        self.nodes.append(node)

        # 3. 엣지(링크) 추출 (Explicit links in metadata)
        explicit_links = frontmatter.get("links", [])
        for target in explicit_links:
            self.links.append({"source": page_id, "target": target, "type": "explicit"})

        # 4. 본문 내 [[WikiLink]] 추출 (Implicit links)
        body_links = re.findall(r"\[\[(.*?)\]\]", content)
        for target in body_links:
            # 중복 링크 방지
            if not any(l["source"] == page_id and l["target"] == target for l in self.links):
                self.links.append({"source": page_id, "target": target, "type": "implicit"})

if __name__ == "__main__":
    # 엔진 단독 테스트용
    engine = KnowledgeEngine()
    graph_data = engine.scan_wiki()
    print(f"Nodes: {len(graph_data['nodes'])}")
    print(f"Links: {len(graph_data['links'])}")
