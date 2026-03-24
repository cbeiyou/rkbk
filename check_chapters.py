"""
题目与答案校对脚本
功能：
1. 逐章对比题目数量和答案数量
2. 检查题目编号与答案编号是否对应
3. 输出校对报告
"""
import os
import re
import sys

# 设置控制台编码
sys.stdout.reconfigure(encoding='utf-8')

# 目录配置
QUESTIONS_DIR = r"E:\project\rk\output\章节演练"
ANSWERS_DIR = r"E:\project\rk\output\参考答案"

# 章节映射（题目文件名 -> 答案文件名）
CHAPTER_MAP = {
    "第一章 信息化发展.md": "第一章信息化发展.md",
    "第二章 信息技术发展.md": "第二章信息技术发展.md",
    "第三章 信息系统治理.md": "第三章信息系统治理.md",
    "第四章 信息系统管理.md": "第四章信息系统管理.md",
    "第五章 信息系统工程.md": "第五章信息系统工程.md",
    "第六章 项目管理概论.md": "第六章项目管理概论.md",
    "第七章 立项管理.md": "第七章立项管理.md",
    "第八章 项目整合管理.md": "第八章项目整合管理.md",
    "第九章 项目范围管理.md": "第九章项目范围管理.md",
    "第十章 项目进度管理.md": "第十章项目进度管理.md",
    "第十一章 项目成本管理.md": "第十一章项目成本管理.md",
    "第十二章 项目质量管理.md": "第十二章项目质量管理.md",
    "第十三章 项目资源管理.md": "第十三章 项目资源管理.md",
    "第十四章 项目沟通管理.md": "第十四章项目沟通管理.md",
    "第十五章 项目风险管理.md": "第十五章项目风险管理.md",
    "第十六章 项目采购管理.md": "第十六章项目采购管理.md",
    "第十七章 项目干系人管理.md": "第十七章项目干系人管理.md",
    "第十八章 项目绩效域.md": "第十八章项目绩效域.md",
    "第十九章 项目配置与变更管理.md": "第十九章项目配置与变更管理.md",
    "第二十章 高级项目管理.md": "第二十章高级项目管理.md",
    "第二十二章 组织通用治理.md": "第二十二章组织通用治理.md",
    "第二十三章 信息系统综合测试与管理.md": "第二十三章信息系统综合测试与管理.md",
    "第二十四章 法律法规与标准规范.md": "第二十四章法律法规与标准规范.md",
}

def extract_question_numbers(file_path):
    """从题目文件提取题号"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 **1、题干** 格式
    pattern = r'\*\*(\d+)、'
    numbers = re.findall(pattern, content)
    return [int(n) for n in numbers]

def extract_answer_numbers(file_path):
    """从答案文件提取题号"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 **1、【答案】 格式
    pattern = r'\*\*(\d+)、【答案】'
    numbers = re.findall(pattern, content)
    return [int(n) for n in numbers]

def check_sequence(numbers):
    """检查编号是否连续"""
    if not numbers:
        return True, []

    expected = list(range(1, max(numbers) + 1))
    missing = [n for n in expected if n not in numbers]
    duplicates = [n for n in numbers if numbers.count(n) > 1]

    issues = []
    if missing:
        issues.append(f"缺失题号: {missing}")
    if duplicates:
        issues.append(f"重复题号: {list(set(duplicates))}")

    return len(issues) == 0, issues

def main():
    print("=" * 60)
    print("题目与答案校对报告")
    print("=" * 60)

    total_questions = 0
    total_answers = 0
    problem_chapters = []

    for q_file, a_file in CHAPTER_MAP.items():
        q_path = os.path.join(QUESTIONS_DIR, q_file)

        print(f"\n【{q_file.replace('.md', '')}】")

        # 提取题目编号
        if os.path.exists(q_path):
            q_numbers = extract_question_numbers(q_path)
            q_count = len(q_numbers)
            total_questions += q_count

            # 检查题目连续性
            q_ok, q_issues = check_sequence(q_numbers)
            if not q_ok:
                for issue in q_issues:
                    print(f"  [!] 题目{issue}")
        else:
            q_numbers = []
            q_count = 0
            print(f"  [X] 题目文件不存在")

        # 提取答案编号
        if a_file:
            a_path = os.path.join(ANSWERS_DIR, a_file)
            if os.path.exists(a_path):
                a_numbers = extract_answer_numbers(a_path)
                a_count = len(a_numbers)
                total_answers += a_count

                # 检查答案连续性
                a_ok, a_issues = check_sequence(a_numbers)
                if not a_ok:
                    for issue in a_issues:
                        print(f"  [!] 答案{issue}")
            else:
                a_numbers = []
                a_count = 0
                print(f"  [X] 答案文件不存在")
        else:
            a_numbers = []
            a_count = 0
            print(f"  [!] 无对应答案文件")

        # 对比数量
        print(f"  题目数: {q_count}, 答案数: {a_count}", end="")

        if a_file is None:
            print(" (跳过)")
            continue

        if q_count == a_count:
            # 检查编号是否对应
            if set(q_numbers) == set(a_numbers):
                print(" [OK] 匹配")
            else:
                q_only = set(q_numbers) - set(a_numbers)
                a_only = set(a_numbers) - set(q_numbers)
                print(" [!] 编号不匹配")
                if q_only:
                    print(f"    题目有但答案无: {sorted(q_only)}")
                if a_only:
                    print(f"    答案有但题目无: {sorted(a_only)}")
                problem_chapters.append(q_file.replace('.md', ''))
        else:
            print(f" [X] 数量不匹配")
            problem_chapters.append(q_file.replace('.md', ''))

    print("\n" + "=" * 60)
    print("汇总统计")
    print("=" * 60)
    print(f"总题目数: {total_questions}")
    print(f"总答案数: {total_answers}")

    if problem_chapters:
        print(f"\n需要人工校对的章节 ({len(problem_chapters)}个):")
        for ch in problem_chapters:
            print(f"  - {ch}")
    else:
        print("\n[OK] 所有章节校对通过！")

if __name__ == "__main__":
    main()