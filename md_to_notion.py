"""
Markdown → Notion 블록 변환 핵심 모듈
upload_all.py, upload_to_subpage.py, watcher.py에서 공통으로 사용
"""

import re

LANG_MAP = {
    'c': 'c', 'cpp': 'c++', 'c++': 'c++',
    'python': 'python', 'py': 'python',
    'javascript': 'javascript', 'js': 'javascript',
    'typescript': 'typescript', 'ts': 'typescript',
    'java': 'java', 'go': 'go', 'rust': 'rust',
    'bash': 'bash', 'shell': 'shell', 'powershell': 'powershell',
    'sql': 'sql', 'html': 'html', 'css': 'css',
    'json': 'json', 'xml': 'plain text', 'mermaid': 'mermaid',
}


def parse_inline(text: str) -> list:
    """볼드(**text**), 인라인 코드(`code`)를 Notion rich_text 형식으로 변환"""
    rich_text = []
    pattern = r'(\*\*[^*]+\*\*|`[^`]+`)'
    parts = re.split(pattern, text)
    for part in parts:
        if not part:
            continue
        if part.startswith('**') and part.endswith('**'):
            rich_text.append({
                "type": "text",
                "text": {"content": part[2:-2]},
                "annotations": {"bold": True}
            })
        elif part.startswith('`') and part.endswith('`') and len(part) > 2:
            rich_text.append({
                "type": "text",
                "text": {"content": part[1:-1]},
                "annotations": {"code": True}
            })
        else:
            rich_text.append({"type": "text", "text": {"content": part}})
    return rich_text if rich_text else [{"type": "text", "text": {"content": ""}}]


def md_to_blocks(content: str) -> list:
    """
    Markdown 문자열을 Notion API 블록 리스트로 변환.

    지원 요소:
    - 제목 (H1, H2, H3)
    - 코드 블록 (언어 감지, 2000자 분할)
    - 표 (헤더 + 구분선 패턴 감지)
    - 인용문 (> 로 시작)
    - 구분선 (---)
    - 볼드, 인라인 코드 인라인 서식
    - 불릿 리스트 (- 또는 * 로 시작)
    - 단락
    """
    blocks = []
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # 코드 블록
        if line.startswith('```'):
            lang = line[3:].strip().lower()
            notion_lang = LANG_MAP.get(lang, 'plain text')
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1
            code_content = '\n'.join(code_lines)
            # Notion 코드 블록은 2000자 제한
            for j in range(0, max(len(code_content), 1), 2000):
                blocks.append({
                    "type": "code",
                    "code": {
                        "language": notion_lang,
                        "rich_text": [{"type": "text", "text": {"content": code_content[j:j+2000]}}]
                    }
                })
            i += 1
            continue

        # 구분선
        if line.strip() == '---':
            blocks.append({"type": "divider", "divider": {}})
            i += 1
            continue

        # 인용문
        if line.startswith('> '):
            blocks.append({
                "type": "quote",
                "quote": {"rich_text": parse_inline(line[2:].strip())}
            })
            i += 1
            continue

        # 표 (헤더 다음 줄이 구분선 패턴인지 확인)
        if '|' in line and i + 1 < len(lines) and re.match(r'^[\|\s\-:]+$', lines[i + 1]):
            headers = [cell.strip() for cell in line.split('|') if cell.strip()]
            i += 2  # 헤더 + 구분선 스킵

            row_blocks = [{
                "type": "table_row",
                "table_row": {
                    "cells": [[{"type": "text", "text": {"content": h}}] for h in headers]
                }
            }]

            while i < len(lines) and '|' in lines[i]:
                cells = [c.strip() for c in lines[i].split('|')][1:-1]
                while len(cells) < len(headers):
                    cells.append('')
                cells = cells[:len(headers)]
                row_blocks.append({
                    "type": "table_row",
                    "table_row": {
                        "cells": [[{"type": "text", "text": {"content": c}}] for c in cells]
                    }
                })
                i += 1

            blocks.append({
                "type": "table",
                "table": {
                    "table_width": len(headers),
                    "has_column_header": True,
                    "has_row_header": False,
                    "children": row_blocks
                }
            })
            continue

        # 불릿 리스트
        if re.match(r'^[\-\*] ', line):
            blocks.append({
                "type": "bulleted_list_item",
                "bulleted_list_item": {"rich_text": parse_inline(line[2:].strip())}
            })

        # 번호 리스트
        elif re.match(r'^\d+\. ', line):
            text = re.sub(r'^\d+\. ', '', line)
            blocks.append({
                "type": "numbered_list_item",
                "numbered_list_item": {"rich_text": parse_inline(text.strip())}
            })

        # 제목
        elif line.startswith('# '):
            blocks.append({"type": "heading_1", "heading_1": {"rich_text": parse_inline(line[2:].strip())}})
        elif line.startswith('## '):
            blocks.append({"type": "heading_2", "heading_2": {"rich_text": parse_inline(line[3:].strip())}})
        elif line.startswith('### '):
            blocks.append({"type": "heading_3", "heading_3": {"rich_text": parse_inline(line[4:].strip())}})

        # 일반 단락
        elif line.strip():
            blocks.append({
                "type": "paragraph",
                "paragraph": {"rich_text": parse_inline(line)}
            })
        else:
            blocks.append({"type": "paragraph", "paragraph": {"rich_text": []}})

        i += 1

    return blocks
