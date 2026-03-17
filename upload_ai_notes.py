import os
from pathlib import Path
from dotenv import load_dotenv
from upload_to_subpage import find_subpage_fuzzy, create_subpage, upload_md, PAGE_ID

load_dotenv()

AI_DIR = Path(__file__).parent / "AI정리"
PARENT_PAGE_NAME = "AI정리"

MD_FILES = [
    "Claude_학습_리소스_개요.md",
    "Claude_개발자_API_활용.md",
    "Claude_업무_활용.md",
    "Claude_프롬프트_엔지니어링.md",
]

if __name__ == "__main__":
    print("'AI정리' 페이지 검색 중...")
    ai_page_id = find_subpage_fuzzy(PAGE_ID, PARENT_PAGE_NAME)

    if ai_page_id:
        print(f"  기존 'AI정리' 페이지 발견 (ID: {ai_page_id})")
    else:
        print("  'AI정리' 페이지 없음 → 새로 생성")
        ai_page_id = create_subpage(PAGE_ID, PARENT_PAGE_NAME)
        print(f"  생성 완료 (ID: {ai_page_id})")

    print(f"\n총 {len(MD_FILES)}개 파일 업로드 시작...\n")
    for filename in MD_FILES:
        filepath = AI_DIR / filename
        if not filepath.exists():
            print(f"  [건너뜀] 파일 없음: {filepath}")
            continue
        upload_md(ai_page_id, str(filepath))

    print("\n완료!")
