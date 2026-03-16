import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')

DIAGRAM_WORDS = {
    # 메모리/시스템 다이어그램 잔재
    '사용자', 'Computer', '운영체제', 'HDD(보조기억장치)', 'CPU', 'RAM(주기억장치)',
    'Program Code', 'Data', 'Heap', 'Free Store', 'Stack',
    # 컴파일 과정 다이어그램
    '고급언어', '전처리', '컴파일', '어셈블리', '링킹',
    # 스트림/파일 다이어그램
    '프로그램', '키보드', 'file', '모니터', 'stdin', 'stdout',
    'スタック', '입력', '출력',
    # 포인터 다이어그램 주소 잔재
    '주소', '칸 값',
    # 기타 단독 다이어그램
    '헤더파일', '소스 코드',
}

C_KEYWORDS = {
    'int', 'char', 'double', 'float', 'void', 'long', 'short',
    'unsigned', 'signed', 'struct', 'union', 'enum', 'typedef',
    'if', 'else', 'for', 'while', 'do', 'switch', 'case',
    'break', 'continue', 'return', 'static', 'extern', 'auto', 'register',
    'const', 'volatile', 'sizeof',
    'NULL', 'EOF', 'FILE',
}

def is_diagram_fragment(line):
    """도형/차트 잔재로 보이는 불릿 판별"""
    if not line.startswith('- '):
        return False
    content = line[2:].strip()

    # 명시적 다이어그램 단어
    if content in DIAGRAM_WORDS:
        return True

    # 1~2글자 (이미 처리됐지만 혹시 몰라서)
    if len(content) <= 2:
        return True

    # 숫자만으로 이루어진 항목 (메모리 주소, 배열 인덱스 잔재)
    if re.match(r'^\d{2,}$', content):
        return True

    # 단일 영문 대문자 1~2자 (A, B, C 등 다이어그램 레이블)
    if re.match(r'^[A-Z]{1,2}$', content):
        return True

    return False

def fix_memory_structure_section(content):
    """메모리 구조 다이어그램 잔재를 깔끔한 설명으로 교체"""
    # "### 1. 메모리 구조" 첫 번째 등장 후 도형 잔재 제거
    lines = content.split('\n')
    result = []
    skip_mode = False
    in_memory_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 메모리 구조 다이어그램 잔재 섹션 감지
        if '컴퓨터의 명령 처리 과정' in line:
            # 이 불릿 이후 도형 잔재들을 노트 박스로 교체
            result.append(line)
            i += 1
            # 다음 빈 줄까지의 단어 조각들 건너뜀
            while i < len(lines) and (is_diagram_fragment(lines[i]) or lines[i].strip() == ''):
                i += 1
            result.append('> 📌 [PPT 참조: 컴퓨터 명령 처리 흐름 — 사용자 → 운영체제 → CPU(RAM) ↔ HDD]')
            result.append('')
            continue

        result.append(line)
        i += 1

    return '\n'.join(result)

def clean_file(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    result = []
    prev_was_blank = False

    for line in lines:
        # 도형 잔재 불릿 제거
        if is_diagram_fragment(line):
            continue

        # 연속 빈 줄 하나로 합치기
        if line.strip() == '':
            if not prev_was_blank:
                result.append('')
            prev_was_blank = True
        else:
            result.append(line)
            prev_was_blank = False

    cleaned = '\n'.join(result)

    # 파일별 추가 정리
    filename = os.path.basename(path)

    if 'Day11' in filename:
        cleaned = fix_memory_structure_section(cleaned)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    return len(lines) - len(result)


# 모든 md 파일 처리
folder = 'C언어_노션_학습자료'
total_removed = 0
for fname in sorted(os.listdir(folder)):
    if not fname.endswith('.md'):
        continue
    path = os.path.join(folder, fname)
    removed = clean_file(path)
    total_removed += removed
    if removed > 0:
        print(f'{fname}: 불필요한 줄 {removed}개 제거')
    else:
        print(f'{fname}: 이상 없음')

print(f'\n총 {total_removed}줄 정리 완료')
