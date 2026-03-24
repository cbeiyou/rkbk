"""
章节文件修正脚本
检查并修正常见问题：
1. 重复的章节标题
2. 缺失的选项
3. 格式问题
"""
import os
import re

OUTPUT_DIR = r"E:\project\rk\output\章节演练"

def fix_chapter_file(file_path):
    """修正单个章节文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    fixed_lines = []

    # 获取章节名称（从文件名）
    chapter_name = os.path.basename(file_path).replace('.md', '')

    # 跳过第一行后的重复章节标题
    for i, line in enumerate(lines):
        # 跳过重复的章节标题行（在第一行"# 章节名"之后出现的纯章节名）
        if i > 0 and line.strip() == chapter_name:
            continue

        # 修正选项格式问题
        # 修复 "A." 等显示为空的问题
        if re.match(r'^  [A-D]\.\s*$', line):
            # 这是不完整的选项行，标记需要人工检查
            line = line + " 【需检查：选项内容缺失】"

        # 修复圆圈数字问题（常见的识别错误）
        line = line.replace('③', '⑤', 1) if line.count('③') > 1 else line

        fixed_lines.append(line)

    # 检查题目完整性
    content = '\n'.join(fixed_lines)

    # 检查每道题是否都有完整的ABCD选项
    questions = re.split(r'\*\*\d+[、．.．]', content)
    issues = []

    for i, q in enumerate(questions[1:], 1):  # 跳过第一个空内容
        # 检查是否有ABCD四个选项
        options = re.findall(r'  [A-D]\.', q)
        if len(options) < 4 and len(options) > 0:
            issues.append(f"第{i}题：选项不完整，只有{len(options)}个选项")

    return content, issues

def main():
    # 获取所有章节文件
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.md') and not f.startswith('progress')]

    print(f"找到 {len(files)} 个章节文件")
    print("="*60)

    all_issues = {}

    for filename in sorted(files):
        file_path = os.path.join(OUTPUT_DIR, filename)
        print(f"\n检查: {filename}")

        fixed_content, issues = fix_chapter_file(file_path)

        if issues:
            all_issues[filename] = issues
            print(f"  发现 {len(issues)} 个问题:")
            for issue in issues[:5]:  # 只显示前5个
                print(f"    - {issue}")
            if len(issues) > 5:
                print(f"    ... 还有 {len(issues)-5} 个问题")
        else:
            print("  无问题")

        # 保存修正后的文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(fixed_content)

    # 输出汇总
    print("\n" + "="*60)
    print("检查完成！")
    print(f"共检查 {len(files)} 个文件")

    if all_issues:
        print(f"\n发现问题的文件: {len(all_issues)}")
        total_issues = sum(len(v) for v in all_issues.values())
        print(f"总问题数: {total_issues}")
    else:
        print("\n所有文件检查通过！")

if __name__ == "__main__":
    main()