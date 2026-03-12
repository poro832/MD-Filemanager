"""
upload_all.py
지정 디렉토리의 모든 .md 파일을 Notion 페이지에 일괄 업로드

사용법:
    python upload_all.py                  # WATCH_DIR 디렉토리 전체
    python upload_all.py ./my_notes       # 특정 디렉토리 지정

.env 설정:
    NOTION_TOKEN=secret_xxx
    PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    WATCH_DIR=.  (선택, 기본값 현재 디렉토리)
"""

import os
import sys
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv
from md_to_notion import md_to_blocks

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
WATCH_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getenv("WATCH_DIR", ".")

notion = Client(auth=NOTION_TOKEN)


def upload_to_notion(filepath: str, parent_page_id: str = PAGE_ID):
    path = Path(filepath)
    title = path.stem
    content = path.read_text(encoding='utf-8-sig', errors='replace')
    if '\x00' in content:
        content = path.read_bytes().decode('utf-16')

    blocks = md_to_blocks(content)

    try:
        new_page = notion.pages.create(
            parent={"page_id": parent_page_id},
            properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
            children=blocks[:100]
        )
        page_id = new_page["id"]
        for i in range(100, len(blocks), 100):
            notion.blocks.children.append(block_id=page_id, children=blocks[i:i+100])
        print(f"  [완료] {title}")
    except Exception as e:
        print(f"  [실패] {title}: {e}")


if __name__ == "__main__":
    md_files = list(Path(WATCH_DIR).glob("*.md"))

    if not md_files:
        print(f"업로드할 .md 파일이 없습니다: {WATCH_DIR}")
    else:
        print(f"총 {len(md_files)}개 파일 → PAGE_ID({PAGE_ID[:8]}...) 업로드 시작\n")
        for f in md_files:
            upload_to_notion(str(f))
        print("\n완료!")
