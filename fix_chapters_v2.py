"""
章节文件深度修正脚本
处理：
1. 缺失选项（跨页问题）
2. 重复章节标题
3. 格式问题
"""
import os
import re

OUTPUT_DIR = r"E:\project\rk\output\章节演练"

def find_incomplete_questions(content):
    """找出选项不完整的题目"""
    # 匹配题目和其选项
    pattern = r'\*\*(\d+)[、．.．]([^*]+)\*\*\n((?:  [A-D]\. [^\n]+\n?)+)'
    matches = re.findall(pattern, content)

    incomplete = []
    for match in matches:
        q_num, q_text, options = match
        # 检查是否有ABCD四个选项
        has_A = '  A.' in options
        has_B = '  B.' in options
        has_C = '  C.' in options
        has_D = '  D.' in options

        missing = []
        if not has_A:
            missing.append('A')
        if not has_B:
            missing.append('B')
        if not has_C:
            missing.append('C')
        if not has_D:
            missing.append('D')

        if missing:
            incomplete.append({
                'num': q_num,
                'text': q_text[:50] + '...' if len(q_text) > 50 else q_text,
                'missing': missing
            })

    return incomplete

def fix_content(content, chapter_name):
    """修正内容"""
    lines = content.split('\n')
    fixed_lines = []
    skip_next = False

    for i, line in enumerate(lines):
        # 跳过重复的章节标题（在Markdown标题之后）
        if i > 1 and line.strip() == chapter_name and not line.startswith('#'):
            continue

        # 修正选项格式
        # 确保选项前有两个空格
        if re.match(r'^[A-D][.．]\s', line):
            line = '  ' + line

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def process_file(file_path):
    """处理单个文件"""
    filename = os.path.basename(file_path)
    chapter_name = filename.replace('.md', '')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 找出不完整的题目
    incomplete = find_incomplete_questions(content)

    # 修正内容
    fixed_content = fix_content(content, chapter_name)

    # 保存
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    return incomplete

def main():
    files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md') and f != 'progress.json'])

    print("=" * 70)
    print("章节文件修正报告")
    print("=" * 70)

    all_incomplete = {}
    total_questions = 0
    total_incomplete = 0

    for filename in files:
        file_path = os.path.join(OUTPUT_DIR, filename)
        incomplete = process_file(file_path)

        # 统计题目数
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        q_count = len(re.findall(r'\*\*\d+[、．.．]', content))
        total_questions += q_count

        if incomplete:
            all_incomplete[filename] = incomplete
            total_incomplete += len(incomplete)
            print(f"\n【{filename}】共 {q_count} 题，{len(incomplete)} 题选项不完整:")
            for q in incomplete[:3]:
                print(f"  第{q['num']}题: 缺少选项 {q['missing']}")
            if len(incomplete) > 3:
                print(f"  ... 还有 {len(incomplete)-3} 题")
        else:
            print(f"【{filename}】共 {q_count} 题，全部完整 ✓")

    # 汇总
    print("\n" + "=" * 70)
    print("汇总统计")
    print("=" * 70)
    print(f"总章节数: {len(files)}")
    print(f"总题目数: {total_questions}")
    print(f"选项不完整题目: {total_incomplete}")
    print(f"完整率: {(total_questions - total_incomplete) * 100 / total_questions:.1f}%")

    if total_incomplete > 0:
        print(f"\n注意: {total_incomplete} 道题目因跨页等原因缺少选项，建议对照原PDF补充")

if __name__ == "__main__":
    main()