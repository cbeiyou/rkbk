"""
PaddleOCR 测试脚本
PaddleOCR 对中文识别效果通常更好
"""
import os
from paddleocr import PaddleOCR
from PIL import Image
import fitz  # PyMuPDF

# 配置
PDF_PATH = r"E:\project\rk\辅导资料\02：章节演练-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\test_output\paddleocr"
TEST_PAGES = 3
SCALE = 2  # 放大倍数

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"正在读取 PDF: {PDF_PATH}")
    print(f"提取前 {TEST_PAGES} 页进行测试")

    # 初始化 PaddleOCR
    print("初始化 PaddleOCR (首次运行需要下载模型)...")
    ocr = PaddleOCR(lang='ch')  # 中文OCR

    # 打开PDF
    doc = fitz.open(PDF_PATH)
    print(f"PDF 总页数: {len(doc)}")

    all_results = []

    for page_num in range(min(TEST_PAGES, len(doc))):
        i = page_num + 1
        print(f"\n{'='*50}")
        print(f"正在处理第 {i} 页...")

        # 渲染页面为图片
        page = doc[page_num]
        mat = fitz.Matrix(SCALE, SCALE)
        pix = page.get_pixmap(matrix=mat)

        # 保存图片
        img_path = os.path.join(OUTPUT_DIR, f"page_{i}.png")
        pix.save(img_path)

        # OCR识别
        result = ocr.predict(img_path)

        # 提取文本
        lines = []
        if result and result[0]:
            for line in result[0]:
                text = line[1][0]  # 文本内容
                confidence = line[1][1]  # 置信度
                lines.append({
                    'text': text,
                    'confidence': confidence
                })

        all_results.append({
            'page': i,
            'lines': lines
        })
        print(f"  识别到 {len(lines)} 行文字")

    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, "paddleocr_result.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# PaddleOCR 识别结果\n\n")
        f.write(f"配置: 放大倍数={SCALE}x, 语言=中文\n\n")
        f.write("---\n\n")

        for r in all_results:
            f.write(f"## 第 {r['page']} 页\n\n")
            for line in r['lines']:
                f.write(f"{line['text']}\n")
            f.write("\n---\n\n")

    print(f"\n结果已保存到: {output_file}")

    # 打印预览
    print("\n" + "="*60)
    print("结果预览（第2页前10行）:")
    print("="*60)
    if len(all_results) >= 2:
        for line in all_results[1]['lines'][:10]:
            print(f"{line['text']} (置信度: {line['confidence']:.2%})")

if __name__ == "__main__":
    main()