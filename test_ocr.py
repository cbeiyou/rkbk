"""
测试 RapidOCR 解析扫描版 PDF
只处理前 2 页，验证效果
"""
import os
import fitz  # PyMuPDF
from rapidocr_onnxruntime import RapidOCR

# 配置
PDF_PATH = r"E:\project\rk\辅导资料\02：章节演练-cp.pdf"
OUTPUT_DIR = r"E:\project\rk\test_output"
TEST_PAGES = 2  # 只测试前2页

def main():
    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"正在读取 PDF: {PDF_PATH}")
    print(f"只提取前 {TEST_PAGES} 页进行测试...")

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
        print(f"\n正在处理第 {i} 页...")

        # 获取页面并转为图片
        page = doc[page_num]
        mat = fitz.Matrix(2, 2)  # 放大2倍提高识别率
        pix = page.get_pixmap(matrix=mat)

        # 保存图片
        img_path = os.path.join(OUTPUT_DIR, f"page_{i}.png")
        pix.save(img_path)
        print(f"  图片已保存: {img_path}")

        # OCR 识别
        result, elapse = ocr(img_path)

        # 提取文字
        page_text = []
        if result is not None and len(result) > 0:
            for line in result:
                # result 格式: [[box, text, confidence], ...]
                text = line[1]
                page_text.append(text)

        # elapse 是字典，包含各阶段耗时
        total_time = sum(elapse.values()) if isinstance(elapse, dict) else 0
        all_results.append({
            'page': i,
            'text': '\n'.join(page_text)
        })
        print(f"  识别到 {len(page_text)} 行文字，耗时: {total_time:.2f}ms")

    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, "ocr_result.md")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# OCR 识别结果\n\n")
        for r in all_results:
            f.write(f"## 第 {r['page']} 页\n\n")
            f.write(r['text'])
            f.write("\n\n---\n\n")

    print(f"\n测试完成！结果已保存到: {output_file}")

    # 打印部分结果预览
    print("\n" + "="*50)
    print("结果预览（第1页前10行）:")
    print("="*50)
    if all_results and all_results[0]['text']:
        lines = all_results[0]['text'].split('\n')[:10]
        for line in lines:
            print(line)

if __name__ == "__main__":
    main()