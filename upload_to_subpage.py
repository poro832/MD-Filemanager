"""
upload_to_subpage.py
Notion 부모 페이지 아래에서 특정 이름의 서브페이지를 찾아 MD 파일을 업로드.
서브페이지가 없으면 자동으로 생성.

사용법:
    python upload_to_subpage.py <md_file_or_dir> <subpage_name>

    예시:
    python upload_to_subpage.py ./notes/intro.md "스프링"
    python upload_to_subpage.py ./AI정리 "AI정리"      # 디렉토리 지정 시 전체 업로드

.env 설정:
    NOTION_TOKEN=secret_xxx
    PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx   (부모 페이지 ID)
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

notion = Client(auth=NOTION_TOKEN)


def find_subpage(parent_id: str, name: str) -> str | None:
    """
    parent_id 하위 페이지 중 제목이 name과 일치하는 페이지 ID 반환.
    없으면 None.
    페이지네이션 지원.
    """
    try:
        cursor = None
        while True:
            kwargs = {"block_id": parent_id}
            if cursor:
                kwargs["start_cursor"] = cursor
            resp = notion.blocks.children.list(**kwargs)
            for block in resp.get("results", []):
                if block.get("type") == "child_page":
                    title = block.get("child_page", {}).get("title", "")
                    if title.strip() == name.strip():
                        return block["id"]
            if resp.get("has_more"):
                cursor = resp.get("next_cursor")
            else:
                break
    except Exception as e:
        print(f"  [검색 오류] {e}")
    return None


def find_subpage_fuzzy(parent_id: str, keyword: str) -> str | None:
    """
    제목에 keyword가 포함된 첫 번째 서브페이지 ID 반환 (부분 일치).
    """
    try:
        cursor = None
        while True:
            kwargs = {"block_id": parent_id}
            if cursor:
                kwargs["start_cursor"] = cursor
            resp = notion.blocks.children.list(**kwargs)
            for block in resp.get("results", []):
                if block.get("type") == "child_page":
                    title = block.get("child_page", {}).get("title", "")
                    if keyword in title:
                        return block["id"]
            if resp.get("has_more"):
                cursor = resp.get("next_cursor")
            else:
                break
    except Exception as e:
        print(f"  [검색 오류] {e}")
    return None


def create_subpage(parent_id: str, title: str) -> str:
    """빈 서브페이지 생성 후 ID 반환"""
    page = notion.pages.create(
        parent={"page_id": parent_id},
        properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}}
    )
    return page["id"]


def upload_md(parent_id: str, filepath: str):
    path = Path(filepath)
    title = path.stem.replace('_', ' ')
    content = path.read_text(encoding='utf-8-sig', errors='replace')
    if '\x00' in content:
        content = path.read_bytes().decode('utf-16')

    blocks = md_to_blocks(content)

    try:
        new_page = notion.pages.create(
            parent={"page_id": parent_id},
            properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
            children=blocks[:100]
        )
        new_id = new_page["id"]
        for i in range(100, len(blocks), 100):
            notion.blocks.children.append(block_id=new_id, children=blocks[i:i+100])
        print(f"  [완료] '{title}' ({len(blocks)}블록)")
    except Exception as e:
        print(f"  [실패] '{title}': {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("사용법: python upload_to_subpage.py <파일_또는_디렉토리> <서브페이지_이름>")
        print("예시:   python upload_to_subpage.py ./notes/intro.md '스프링'")
        sys.exit(1)

    target = Path(sys.argv[1])
    subpage_name = sys.argv[2]

    if not target.exists():
        print(f"경로 없음: {target}")
        sys.exit(1)

    # 서브페이지 탐색 또는 생성
    print(f"'{subpage_name}' 서브페이지 탐색 중...")
    subpage_id = find_subpage(PAGE_ID, subpage_name)

    if subpage_id:
        print(f"  발견 (ID: {subpage_id})")
    else:
        print(f"  없음 → 새로 생성")
        subpage_id = create_subpage(PAGE_ID, subpage_name)
        print(f"  생성 완료 (ID: {subpage_id})")

    # 업로드
    if target.is_dir():
        md_files = list(target.rglob("*.md"))
        if not md_files:
            print(f"디렉토리에 .md 파일이 없습니다: {target}")
            sys.exit(0)
        print(f"\n총 {len(md_files)}개 파일 업로드 시작...\n")
        for f in md_files:
            upload_md(subpage_id, str(f))
    else:
        print(f"\n'{target.name}' 업로드 중...")
        upload_md(subpage_id, str(target))

    print("\n완료!")
