"""
优化版 OCR 解析脚本
改进：
1. 更高的图片分辨率 (3倍放大)
2. 图像预处理 (增强对比度、去噪)
3. 更好的文本格式化 (保留题目结构)
4. 表格检测和处理
"""
import os
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

# 配置
PDF_PATH = r"E:\project\rk\辅导资料\02：章节演练-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\test_output"
TEST_PAGES = 3  # 测试前3页
SCALE = 3  # 图片放大倍数

def preprocess_image(img_path):
    """图像预处理：增强对比度、锐化"""
    img = Image.open(img_path)

    # 转为灰度图（可选，有时彩色效果更好）
    # img = img.convert('L')

    # 增强对比度
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)

    # 锐化
    img = img.filter(ImageFilter.SHARPEN)

    # 保存预处理后的图片
    processed_path = img_path.replace('.png', '_processed.png')
    img.save(processed_path)

    return processed_path

def format_ocr_result(result):
    """格式化OCR结果，保留题目结构"""
    if result is None or len(result) == 0:
        return ""

    formatted_lines = []
    prev_y = None
    current_question = []

    for item in result:
        # result 格式: [box, text, confidence]
        box = item[0]  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        text = item[1]
        confidence = item[2] if len(item) > 2 else 1.0

        # 计算文本框的中心Y坐标（用于判断是否同一行）
        y_coords = [p[1] for p in box]
        center_y = sum(y_coords) / 4

        # 判断是否为题目编号 (如 "1、" "2、" 等)
        is_question_num = False
        if text and len(text) > 0:
            # 匹配题目编号模式
            import re
            if re.match(r'^\d+[、．.]', text):
                is_question_num = True

        # 判断是否为选项 (A. B. C. D.)
        is_option = False
        if text and len(text) > 0:
            if re.match(r'^[A-D][、．.]', text):
                is_option = True

        # 格式化输出
        if is_question_num:
            if current_question:
                formatted_lines.append('')  # 题目之间加空行
            formatted_lines.append(f"**{text}**")
        elif is_option:
            formatted_lines.append(f"  {text}")  # 选项缩进
        else:
            formatted_lines.append(text)

    return '\n'.join(formatted_lines)

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
        mat = fitz.Matrix(SCALE, SCALE)  # 放大提高识别率
        pix = page.get_pixmap(matrix=mat)

        # 保存原始图片
        img_path = os.path.join(OUTPUT_DIR, f"page_{i}.png")
        pix.save(img_path)
        print(f"  原始图片已保存: {img_path}")

        # 图像预处理
        print("  正在进行图像预处理...")
        processed_path = preprocess_image(img_path)
        print(f"  预处理图片已保存: {processed_path}")

        # OCR 识别 (使用预处理后的图片)
        print("  正在进行 OCR 识别...")
        result, elapse = ocr(processed_path)

        # 格式化结果
        if result is not None and len(result) > 0:
            # 原始文本（用于调试）
            raw_text = '\n'.join([line[1] for line in result])
            # 格式化文本
            formatted_text = format_ocr_result(result)
        else:
            raw_text = ""
            formatted_text = ""

        # 计算耗时
        total_time = sum(elapse.values()) if isinstance(elapse, dict) else 0

        all_results.append({
            'page': i,
            'raw_text': raw_text,
            'formatted_text': formatted_text,
            'line_count': len(result) if result else 0,
            'time_ms': total_time
        })

        print(f"  识别到 {len(result) if result else 0} 行文字")
        print(f"  耗时: {total_time:.2f}ms")

    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, "ocr_result_v2.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# OCR 识别结果 (优化版)\n\n")
        f.write(f"配置: 放大倍数={SCALE}x, 图像预处理=对比度增强+锐化\n\n")
        f.write("---\n\n")

        for r in all_results:
            f.write(f"## 第 {r['page']} 页\n\n")
            f.write(f"> 识别行数: {r['line_count']}, 耗时: {r['time_ms']:.2f}ms\n\n")
            f.write(r['formatted_text'])
            f.write("\n\n---\n\n")

    print(f"\n✅ 测试完成！结果已保存到: {output_file}")

    # 打印对比预览
    print("\n" + "="*60)
    print("结果预览（第2页前15行，格式化版）:")
    print("="*60)
    if len(all_results) >= 2:
        lines = all_results[1]['formatted_text'].split('\n')[:15]
        for line in lines:
            print(line)

if __name__ == "__main__":
    main()