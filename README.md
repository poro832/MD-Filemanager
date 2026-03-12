# MD-Filemanager

Markdown 파일을 Notion 페이지에 업로드하는 Python 스크립트 모음.

## 기능

| 스크립트 | 설명 |
|----------|------|
| `upload_all.py` | 디렉토리 내 모든 `.md` 파일을 Notion 페이지에 일괄 업로드 |
| `upload_to_subpage.py` | 특정 서브페이지를 찾아(없으면 생성) MD 파일 업로드 |
| `watcher.py` | 디렉토리를 감시하다가 새 `.md` 파일 생성 시 자동 업로드 |
| `md_to_notion.py` | Markdown → Notion 블록 변환 공통 모듈 |

## 지원하는 Markdown 요소

- 제목 H1 / H2 / H3
- **볼드**, `인라인 코드`
- 코드 블록 (언어 감지, 2000자 자동 분할)
- 표 (헤더 + 구분선 패턴)
- 불릿 리스트 / 번호 리스트
- 인용문 (`>`)
- 구분선 (`---`)

## 설치

```bash
pip install -r requirements.txt
```

## 설정

`.env.example`을 복사해 `.env`로 만들고 값을 채운다.

```bash
cp .env.example .env
```

```env
NOTION_TOKEN=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PAGE_ID=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WATCH_DIR=.
```

### Notion Integration 설정 방법

1. https://www.notion.so/my-integrations 에서 Integration 생성
2. 발급된 `Internal Integration Token`을 `NOTION_TOKEN`에 입력
3. 업로드할 Notion 페이지를 열고 우측 상단 `...` → `Connections`에서 Integration 추가
4. 페이지 URL에서 ID 추출: `notion.so/페이지명-{32자리ID}` → `PAGE_ID`에 입력

## 사용법

### 전체 업로드

```bash
# 현재 디렉토리의 모든 .md 파일 업로드
python upload_all.py

# 특정 디렉토리 지정
python upload_all.py ./my_notes
```

### 서브페이지에 업로드

```bash
# 단일 파일 → "스프링" 서브페이지 안에 업로드 (없으면 생성)
python upload_to_subpage.py ./notes/intro.md "스프링"

# 디렉토리 전체 → "AI정리" 서브페이지 안에 업로드
python upload_to_subpage.py ./AI정리 "AI정리"
```

### 자동 감시 (watcher)

```bash
# 현재 디렉토리 감시
python watcher.py

# 특정 디렉토리 감시
python watcher.py ./my_notes
```

새 `.md` 파일을 저장하면 자동으로 Notion에 업로드된다. `Ctrl+C`로 종료.
