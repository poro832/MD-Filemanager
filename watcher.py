import time
import os
import sys
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from notion_client import Client
from dotenv import load_dotenv
from md_to_notion import md_to_blocks

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")
WATCH_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getenv("WATCH_DIR", ".")

notion = Client(auth=NOTION_TOKEN)


def upload_to_notion(filepath: str):
    path = Path(filepath)
    if path.suffix != '.md':
        return

    title = path.stem
    content = path.read_text(encoding='utf-8-sig', errors='replace')
    if '\x00' in content:
        content = path.read_bytes().decode('utf-16')

    blocks = md_to_blocks(content)

    try:
        new_page = notion.pages.create(
            parent={"page_id": PAGE_ID},
            properties={"title": {"title": [{"type": "text", "text": {"content": title}}]}},
            children=blocks[:100]
        )
        page_id = new_page["id"]
        for i in range(100, len(blocks), 100):
            notion.blocks.children.append(block_id=page_id, children=blocks[i:i+100])
        print(f"[완료] {title}")
    except Exception as e:
        print(f"[실패] {title}: {e}")


class MDHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            print(f"[감지] {event.src_path}")
            time.sleep(0.5)  # 파일 쓰기 완료 대기
            upload_to_notion(event.src_path)


if __name__ == "__main__":
    watch_path = str(Path(WATCH_DIR).resolve())
    print(f"[감시 시작] {watch_path}")
    print("새 .md 파일 생성 시 자동 업로드됩니다. (종료: Ctrl+C)\n")

    event_handler = MDHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_path, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[종료] 감시 종료")
        observer.stop()
    observer.join()
