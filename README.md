# MD-Filemanager

학습 자료(Markdown)를 Notion 페이지로 정리/업로드하기 위한 도구 모음 + 정리 포맷 가이드.

## 정리 방식 개요

학습 자료는 **두 가지 경로**로 Notion에 정리한다.

```
            ┌─────────────────────────────────┐
            │   학습 주제 (자격증 / 강의 등)    │
            └────────────────┬────────────────┘
                             │
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
┌──────────────────────┐              ┌──────────────────────┐
│ ① Claude Code +      │              │ ② 로컬 .md 파일 작성 │
│    Notion MCP 직접   │              │   → 본 레포 스크립트  │
│    페이지 생성        │              │     로 일괄 업로드    │
└──────────┬───────────┘              └──────────┬───────────┘
           └──────────────────┬───────────────────┘
                              ▼
                  ┌────────────────────────┐
                  │   Notion (단일 SoT)     │
                  └────────────────────────┘
```

> 어떤 경로를 사용하든 [`FORMAT_GUIDE.md`](./FORMAT_GUIDE.md)의 표준 포맷을 따른다.

## 표준 정리 포맷

자세한 규칙은 [`FORMAT_GUIDE.md`](./FORMAT_GUIDE.md) 참고. 핵심 요약:

- 제목은 `<주제명> 핵심 개념 정리` + 이모지 아이콘
- 첫 줄에 `> 한 줄 요약 + 출제 기준` 인용문
- `# 📋 시험 개요` 섹션에 시험코드/문항수/합격기준/출제 영역 표
- 도메인별 H1 (1️⃣ 2️⃣ 3️⃣ ...) → 소주제별 H2 (이모지 + 제목) → 세부 H3
- 비교/대조는 반드시 **표**로
- 마지막에 `# 📝 시험 대비 팁` 섹션 + 마지막 업데이트 날짜

### 적용 사례
- 정보처리산업기사 핵심 개념 정리 📘
- SQLD 핵심 개념 정리 🗄️
- AWS Solutions Architect Associate (SAA) ☁️
- AWS AI Practitioner (AIF-C01) 🤖
- 자료구조 / C언어 / 스프링 / 알고리즘 / 클라우드 등

## 스크립트 기능

| 스크립트 | 설명 |
|----------|------|
| `upload_all.py` | 디렉토리 내 모든 `.md` 파일을 Notion 페이지에 일괄 업로드 |
| `upload_to_subpage.py` | 특정 서브페이지를 찾아(없으면 생성) MD 파일 업로드 |
| `watcher.py` | 디렉토리를 감시하다가 새 `.md` 파일 생성 시 자동 업로드 |
| `md_to_notion.py` | Markdown → Notion 블록 변환 공통 모듈 |
| `cleanup_notion_md.py` | MD 파일 내 불필요한 도형/차트 잔재 자동 정리 |

## 지원하는 Markdown 요소

- 제목 H1 / H2 / H3 / H4(볼드 단락으로 변환, `(계속)` 항목 자동 제거)
- **볼드**, `인라인 코드` 인라인 서식
- 코드 블록 (언어 감지, 2000자 자동 분할)
- 표 (헤더 + 구분선 패턴)
- 불릿 리스트 (들여쓰기 중첩 지원) / 번호 리스트
- callout 블록 (`> 📌` / `> 💡`)
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

### ① Claude Code + Notion MCP (권장: 신규 작성)

Claude와 대화하며 학습 노트를 즉시 Notion에 생성하는 방식.

1. Claude Code에서 Notion MCP 연동 (`claude_ai_Notion`)
2. 프롬프트 예시:
   ```
   <주제> 핵심 개념을 FORMAT_GUIDE.md 포맷에 맞춰 정리해서 노션에 올려줘
   ```
3. Claude가 `notion-create-pages` 도구로 직접 페이지 생성

### ② 로컬 .md → 일괄 업로드

```bash
# 현재 디렉토리의 모든 .md 파일 업로드
python upload_all.py

# 특정 디렉토리 지정
python upload_all.py ./my_notes

# 기존 동일 제목 페이지 삭제 후 재업로드 (수정 내용 반영 시)
python upload_all.py ./my_notes --clean
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

### MD 파일 정리 (업로드 전 전처리)

```bash
# PPT 변환 등으로 생긴 도형/차트 잔재 제거
python cleanup_notion_md.py
```

`cleanup_notion_md.py` 내 `folder` 변수를 정리할 디렉토리 경로로 수정 후 실행.
