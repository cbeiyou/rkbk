"""
优化版 OCR 解析脚本 v3
改进：
1. 更高的图片分辨率 (3倍放大)
2. 图像预处理 (增强对比度、锐化)
3. 后处理：修复常见OCR错误
4. 更好的文本格式化
"""
import os
import re
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# 配置
PDF_PATH = r"E:\project\rk\辅导资料\02：章节演练-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\test_output"
TEST_PAGES = 5  # 测试前5页
SCALE = 3  # 图片放大倍数

# 常见OCR错误修正字典
OCR_CORRECTIONS = {
    '李生虚拟化': '孪生虚拟化',
    '数字李生': '数字孪生',
    'laaS': 'IaaS',
    'laas': 'IaaS',
    '1aaS': 'IaaS',
    '1oV': 'IoV',
    'PaaS和SaaS': 'PaaS和SaaS',
    'Paa S': 'PaaS',
    'Saa S': 'SaaS',
    # 选项格式修正
    '.A.': 'A.',
    '.B.': 'B.',
    '.C.': 'C.',
    '.D.': 'D.',
    'A．': 'A.',
    'B．': 'B.',
    'C．': 'C.',
    'D．': 'D.',
    # 圆圈数字修正 (常见于选择题组合选项)
    '036': '①③⑥',
    '046': '①④⑥',
    '234': '②③④',
    '236': '②③⑥',
    '136': '①③⑥',
    '146': '①④⑥',
    '124': '①②④',
    '125': '①②⑤',
    '135': '①③⑤',
    '145': '①④⑤',
    '235': '②③⑤',
    '245': '②④⑤',
}

def preprocess_image(img_path):
    """图像预处理：增强对比度、锐化"""
    img = Image.open(img_path)

    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # 锐化
    img = img.filter(ImageFilter.SHARPEN)

    # 保存预处理后的图片
    processed_path = img_path.replace('.png', '_processed.png')
    img.save(processed_path)

    return processed_path

def correct_text(text):
    """修正OCR识别错误"""
    for wrong, correct in OCR_CORRECTIONS.items():
        text = text.replace(wrong, correct)
    return text

def format_question(text_lines):
    """格式化题目，合并跨行文本"""
    formatted = []
    i = 0
    while i < len(text_lines):
        line = text_lines[i]

        # 检测题目编号 (如 "1、" "2、")
        if re.match(r'^\d+[、．.．]\s*', line):
            # 合并题目内容直到下一个选项或下一题
            question_parts = [line]
            i += 1
            while i < len(text_lines):
                next_line = text_lines[i]
                # 如果是选项或下一题，停止
                if re.match(r'^[A-D][、．.．\s]', next_line) or re.match(r'^\d+[、．.．]\s*', next_line):
                    break
                # 如果是页脚，跳过
                if '软考' in next_line or '羽仪' in next_line:
                    i += 1
                    continue
                question_parts.append(next_line)
                i += 1
            formatted.append(f"**{' '.join(question_parts)}**")

        # 检测选项
        elif re.match(r'^[A-Da-d][、．.．\s]', line):
            # 标准化选项格式：大写字母 + 点
            line = re.sub(r'^([A-Da-d])[、．.．]\s*', lambda m: f"{m.group(1).upper()}. ", line)
            formatted.append(f"  {line}")
            i += 1

        # 其他文本
        else:
            # 跳过页脚
            if '软考' in line or '羽仪' in line or '学历' in line or '入户' in line:
                i += 1
                continue
            formatted.append(line)
            i += 1

    return formatted

def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"正在读取 PDF: {PDF_PATH}")
    print(f"提取前 {TEST_PAGES} 页进行测试，放大倍数: {SCALE}x")

    # 使用 PyMuPDF 打开 PDF
    doc = fitz.open(PDF_PATH)
    print(f"PDF 总页数: {len(doc)}")

    # 初始化 RapidOCR
    print("初始化 RapidOCR...")
    ocr = RapidOCR()

    # 处理每一页
    all_results = []
    for page_num in range(min(TEST_PAGES, len(doc))):
        i = page_num + 1
        print(f"\n{'='*50}")
        print(f"正在处理第 {i} 页...")
        print('='*50)

        # 获取页面并转为图片
        page = doc[page_num]
        mat = fitz.Matrix(SCALE, SCALE)
        pix = page.get_pixmap(matrix=mat)

        # 保存原始图片
        img_path = os.path.join(OUTPUT_DIR, f"page_{i}.png")
        pix.save(img_path)

        # 图像预处理
        processed_path = preprocess_image(img_path)

        # OCR 识别
        result, elapse = ocr(processed_path)

        # 提取并修正文本
        text_lines = []
        if result is not None and len(result) > 0:
            for line in result:
                text = line[1]
                # 修正错误
                text = correct_text(text)
                text_lines.append(text)

        # 格式化
        formatted_lines = format_question(text_lines)

        # 计算耗时
        total_time = sum(elapse.values()) if isinstance(elapse, dict) else 0

        all_results.append({
            'page': i,
            'formatted_lines': formatted_lines,
            'line_count': len(result) if result else 0,
            'time_ms': total_time
        })

        print(f"  识别到 {len(result) if result else 0} 行文字，耗时: {total_time:.2f}ms")

    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, "ocr_result_v3.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# OCR 识别结果 (优化版 v3)\n\n")
        f.write(f"配置: 放大倍数={SCALE}x, 图像预处理=对比度增强+锐化, 后处理=常见错误修正\n\n")
        f.write("---\n\n")

        for r in all_results:
            f.write(f"## 第 {r['page']} 页\n\n")
            f.write(f"> 识别行数: {r['line_count']}, 耗时: {r['time_ms']:.2f}ms\n\n")
            for line in r['formatted_lines']:
                f.write(f"{line}\n")
            f.write("\n---\n\n")

    print(f"\n测试完成！结果已保存到: {output_file}")

    # 打印对比
    print("\n" + "="*60)
    print("结果预览（第2页，前20行）:")
    print("="*60)
    if len(all_results) >= 2:
        for line in all_results[1]['formatted_lines'][:20]:
            print(line)

if __name__ == "__main__":
    main()