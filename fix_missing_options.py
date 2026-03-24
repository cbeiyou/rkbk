"""
补充缺失选项脚本
从原始PDF中提取缺失选项
"""
import os
import re
import fitz
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageEnhance, ImageFilter

PDF_PATH = r"E:\project\rk\辅导资料\02：章节演练-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\output\章节演练"
SCALE = 3

# 初始化OCR
ocr = RapidOCR()

def preprocess_image(img_path):
    img = Image.open(img_path)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def get_page_text(page_num):
    """获取指定页的OCR文本"""
    doc = fitz.open(PDF_PATH)
    page = doc[page_num]
    mat = fitz.Matrix(SCALE, SCALE)
    pix = page.get_pixmap(matrix=mat)

    # 预处理
    img = preprocess_image(pix)
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        img.save(tmp.name)
        result, _ = ocr(tmp.name)
        os.unlink(tmp.name)

    if result:
        return [line[1] for line in result]
    return []

def find_question_options(text_lines, q_num):
    """在文本行中找到指定题号的所有选项"""
    options = {}
    in_question = False

    for i, line in enumerate(text_lines):
        # 找到题目
        if re.match(rf'^{q_num}[、．.．]', line):
            in_question = True
            continue

        if in_question:
            # 找到选项
            match = re.match(r'^([A-D])[、．.．\s]+(.+)', line)
            if match:
                opt_letter = match.group(1)
                opt_text = match.group(2)
                options[opt_letter] = opt_text
            # 遇到下一题，停止
            elif re.match(r'^\d+[、．.．]', line):
                break

    return options

def fix_chapter(filename, issues):
    """修正章节文件"""
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 这里需要根据题目所在页码来补充
    # 由于题目跨页，我们标记需要人工检查的位置
    for q_num, missing in issues:
        # 在缺失选项的位置添加标记
        pattern = rf'(\*\*{q_num}[、．.．][^*]+\*\*\n)((?:  [A-D]\. [^\n]+\n?)+)'
        def add_marker(match):
            question = match.group(1)
            options = match.group(2)
            # 添加缺失选项占位符
            for opt in missing:
                if f'  {opt}.' not in options:
                    options += f"  {opt}. 【需补充：跨页丢失】\n"
            return question + options

        content = re.sub(pattern, add_marker, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    return len(issues)

def main():
    # 先扫描所有章节，找出缺失选项
    all_issues = {}

    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md') and f != 'progress.json'])

    for filename in files:
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        questions = re.split(r'\*\*(\d+)[、．.]', content)[1:]
        issues = []

        for i in range(0, len(questions), 2):
            if i+1 >= len(questions):
                break
            q_num = questions[i]
            q_content = questions[i+1]

            missing = []
            if '  A.' not in q_content: missing.append('A')
            if '  B.' not in q_content: missing.append('B')
            if '  C.' not in q_content: missing.append('C')
            if '  D.' not in q_content: missing.append('D')

            if missing:
                issues.append((q_num, missing))

        if issues:
            all_issues[filename] = issues

    # 修正每个章节
    print("正在标记缺失选项...")
    total_fixed = 0
    for filename, issues in all_issues.items():
        fixed = fix_chapter(filename, issues)
        total_fixed += fixed
        print(f"  {filename}: 标记 {fixed} 处")

    print(f"\n完成！共标记 {total_fixed} 处缺失选项")
    print("这些位置已用【需补充：跨页丢失】标记，请对照原PDF补充")

if __name__ == "__main__":
    main()