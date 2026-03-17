import os
from pathlib import Path
from dotenv import load_dotenv
from upload_to_subpage import find_subpage_fuzzy, upload_md, notion, PAGE_ID

load_dotenv()

TARGET_MD = Path(__file__).parent / "스프링" / "스프링_소개_및_기본이론.md"


def find_spring_page_via_search():
    """Notion 검색 API로 스프링 페이지 찾기 (제목 정확 일치)"""
    try:
        results = notion.search(query="스프링", filter={"value": "page", "property": "object"})
        for page in results.get("results", []):
            props = page.get("properties", {})
            title_list = props.get("title", {}).get("title", [])
            title = "".join(t.get("plain_text", "") for t in title_list)
            print(f"  검색 결과: '{title}' ID={page['id']}")
            if title.strip() == "스프링":
                print(f"  => 스프링 페이지 발견! ID: {page['id']}")
                return page["id"]
    except Exception as e:
        print(f"  검색 오류: {e}")
    return None


if __name__ == "__main__":
    if not TARGET_MD.exists():
        print(f"파일 없음: {TARGET_MD}")
        exit(1)

    print("=== 검색 API로 스프링 페이지 찾기 ===")
    spring_page_id = find_spring_page_via_search()

    if not spring_page_id:
        print("\n=== 자식 목록으로 스프링 페이지 찾기 ===")
        spring_page_id = find_subpage_fuzzy(PAGE_ID, "스프링")

    if spring_page_id:
        print("\n스프링 페이지에 업로드 중...")
        upload_md(spring_page_id, str(TARGET_MD))
    else:
        print("\n스프링 페이지를 찾지 못했습니다. 학습용 페이지에 직접 업로드합니다.")
        upload_md(PAGE_ID, str(TARGET_MD))
