"""
高项讲义PDF处理脚本
功能：
1. OCR识别讲义PDF
2. 按章节分文件保存
3. 支持中断恢复
"""
import os
import re
import json
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageEnhance, ImageFilter

# 配置
PDF_PATH = r"E:\project\rk\辅导资料\01：高项讲义-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\output\高项讲义"
SCALE = 3  # 图片放大倍数

# 进度文件
PROGRESS_FILE = os.path.join(OUTPUT_DIR, "progress.json")

# 常见OCR错误修正字典
OCR_CORRECTIONS = {
    '李生虚拟化': '孪生虚拟化',
    '数字李生': '数字孪生',
    'laaS': 'IaaS',
    'laas': 'IaaS',
    '1aaS': 'IaaS',
    '1oV': 'IoV',
    'Paa S': 'PaaS',
    'Saa S': 'SaaS',
    'A．': 'A.',
    'B．': 'B.',
    'C．': 'C.',
    'D．': 'D.',
}

# 章节标题匹配模式
CHAPTER_PATTERNS = [
    r'^第[一二三四五六七八九十百]+章',
    r'^第\d+章',
]

def preprocess_image(img_path):
    """图像预处理"""
    img = Image.open(img_path)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    img = img.filter(ImageFilter.SHARPEN)
    processed_path = img_path.replace('.png', '_processed.png')
    img.save(processed_path)
    return processed_path

def correct_text(text):
    """修正OCR错误"""
    for wrong, correct in OCR_CORRECTIONS.items():
        text = text.replace(wrong, correct)
    return text

def is_chapter_title(line):
    """判断是否为章节标题"""
    for pattern in CHAPTER_PATTERNS:
        if re.match(pattern, line):
            return True
    return False

def filter_watermark(text_lines):
    """过滤水印行"""
    filtered = []
    for line in text_lines:
        if '软考' in line or '羽仪' in line or '学历' in line or '入户' in line:
            continue
        filtered.append(line)
    return filtered

def load_progress():
    """加载进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'last_page': 0, 'chapters': {}}

def save_progress(progress):
    """保存进度"""
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"正在处理: {PDF_PATH}")
    print(f"输出目录: {OUTPUT_DIR}")

    doc = fitz.open(PDF_PATH)
    total_pages = len(doc)
    print(f"PDF总页数: {total_pages}")

    # 加载进度
    progress = load_progress()
    start_page = progress.get('last_page', 0)

    if start_page > 0:
        print(f"从第 {start_page + 1} 页继续处理...")

    # 初始化OCR
    print("初始化 RapidOCR...")
    ocr = RapidOCR()

    # 当前章节
    current_chapter = "目录"
    chapter_content = []

    # 处理每一页
    for page_num in range(start_page, total_pages):
        i = page_num + 1
        print(f"\r处理进度: {i}/{total_pages} ({i*100//total_pages}%)", end='', flush=True)

        try:
            page = doc[page_num]
            mat = fitz.Matrix(SCALE, SCALE)
            pix = page.get_pixmap(matrix=mat)

            # 保存图片
            img_dir = os.path.join(OUTPUT_DIR, "images")
            os.makedirs(img_dir, exist_ok=True)
            img_path = os.path.join(img_dir, f"page_{i}.png")
            pix.save(img_path)

            # 预处理
            processed_path = preprocess_image(img_path)

            # OCR
            result, _ = ocr(processed_path)

            # 提取文本
            text_lines = []
            if result is not None and len(result) > 0:
                for line in result:
                    text = correct_text(line[1])
                    text_lines.append(text)

            # 检测章节标题
            for line in text_lines:
                if is_chapter_title(line):
                    # 保存上一章节
                    if chapter_content:
                        chapter_file = os.path.join(OUTPUT_DIR, f"{current_chapter}.md")
                        with open(chapter_file, 'w', encoding='utf-8') as f:
                            f.write(f"# {current_chapter}\n\n")
                            for l in chapter_content:
                                f.write(f"{l}\n")
                        progress['chapters'][current_chapter] = len(chapter_content)
                        chapter_content = []

                    current_chapter = line
                    print(f"\n发现章节: {current_chapter}")

            # 过滤水印并添加到章节内容
            filtered = filter_watermark(text_lines)
            chapter_content.extend(filtered)

            # 清理临时图片
            if os.path.exists(processed_path):
                os.remove(processed_path)

            # 每10页保存一次进度
            if i % 10 == 0:
                progress['last_page'] = page_num
                save_progress(progress)

        except Exception as e:
            print(f"\n处理第 {i} 页时出错: {e}")
            progress['last_page'] = page_num
            save_progress(progress)
            continue

    # 保存最后章节
    if chapter_content:
        chapter_file = os.path.join(OUTPUT_DIR, f"{current_chapter}.md")
        with open(chapter_file, 'w', encoding='utf-8') as f:
            f.write(f"# {current_chapter}\n\n")
            for l in chapter_content:
                f.write(f"{l}\n")
        progress['chapters'][current_chapter] = len(chapter_content)

    # 更新进度
    progress['last_page'] = total_pages
    progress['completed'] = True
    save_progress(progress)

    print(f"\n\n处理完成！")
    print(f"共处理 {total_pages} 页，生成 {len(progress['chapters'])} 个章节文件")
    print(f"输出目录: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()