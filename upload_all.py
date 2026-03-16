"""
upload_all.py
지정 디렉토리의 모든 .md 파일을 Notion 페이지에 일괄 업로드

사용법:
    python upload_all.py                      # WATCH_DIR 디렉토리 전체
    python upload_all.py ./my_notes           # 특정 디렉토리 지정
    python upload_all.py ./my_notes --clean   # 기존 동일 제목 페이지 삭제 후 재업로드

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

args = [a for a in sys.argv[1:] if not a.startswith('--')]
flags = [a for a in sys.argv[1:] if a.startswith('--')]

WATCH_DIR = args[0] if args else os.getenv("WATCH_DIR", ".")
CLEAN = '--clean' in flags

notion = Client(auth=NOTION_TOKEN)


def get_existing_pages(parent_id: str) -> dict:
    """부모 페이지의 자식 페이지 목록을 {제목: id} 형태로 반환"""
    pages = {}
    cursor = None
    while True:
        kwargs = {"block_id": parent_id}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = notion.blocks.children.list(**kwargs)
        for block in resp.get("results", []):
            if block.get("type") == "child_page":
                title = block.get("child_page", {}).get("title", "")
                pages[title] = block["id"]
        if resp.get("has_more"):
            cursor = resp.get("next_cursor")
        else:
            break
    return pages


def upload_to_notion(filepath: str, parent_page_id: str = PAGE_ID, existing: dict = None):
    path = Path(filepath)
    title = path.stem
    content = path.read_text(encoding='utf-8-sig', errors='replace')
    if '\x00' in content:
        content = path.read_bytes().decode('utf-16')

    # --clean 옵션: 기존 동일 제목 페이지 삭제
    if existing and title in existing:
        try:
            notion.pages.update(page_id=existing[title], archived=True)
            print(f"  [삭제] 기존 '{title}' 페이지")
        except Exception as e:
            print(f"  [삭제 실패] '{title}': {e}")

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
        print(f"  [완료] {title} ({len(blocks)}블록)")
    except Exception as e:
        print(f"  [실패] {title}: {e}")


if __name__ == "__main__":
    md_files = list(Path(WATCH_DIR).glob("*.md"))

    if not md_files:
        print(f"업로드할 .md 파일이 없습니다: {WATCH_DIR}")
    else:
        existing = get_existing_pages(PAGE_ID) if CLEAN else {}
        if CLEAN:
            print(f"[--clean] 기존 페이지 {len(existing)}개 확인됨\n")

        print(f"총 {len(md_files)}개 파일 → PAGE_ID({PAGE_ID[:8]}...) 업로드 시작\n")
        for f in sorted(md_files):
            upload_to_notion(str(f), existing=existing)
        print("\n완료!")
