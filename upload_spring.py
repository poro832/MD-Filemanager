import os
from pathlib import Path
from dotenv import load_dotenv
from upload_to_subpage import find_subpage_fuzzy, upload_md, notion, PAGE_ID

load_dotenv()

TARGET_MD = "스프링_웹_MVC_프로젝트의_구조.md"

if __name__ == "__main__":
    md_path = Path(__file__).parent / TARGET_MD
    if not md_path.exists():
        print(f"파일 없음: {md_path}")
        exit(1)

    print("스프링 페이지 검색 중...")
    spring_page_id = find_subpage_fuzzy(PAGE_ID, "스프링")

    if spring_page_id:
        print(f"스프링 페이지에 업로드 중...")
        upload_md(spring_page_id, str(md_path))
    else:
        print("스프링 페이지를 찾지 못했습니다. 학습용 페이지에 직접 업로드합니다.")
        upload_md(PAGE_ID, str(md_path))
