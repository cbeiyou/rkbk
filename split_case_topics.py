#!/usr/bin/env python3
"""
案例专题文档拆分脚本
将OCR识别的案例专题Markdown按章节、题目、答案拆分
"""

import os
import re

# 输入输出路径
INPUT_FILE = "辅导资料/04：案例专题-cp.md"
OUTPUT_DIR = "output/案例专题"
TITLE_OUTPUT_DIR = f"{OUTPUT_DIR}/题目"
ANSWER_OUTPUT_DIR = f"{OUTPUT_DIR}/参考答案"

# 专题列表（不含"第一篇答题技巧"）
TOPICS = [
    "专题一整合管理",
    "专题二范围管理",
    "专题三进度管理",
    "专题四成本管理",
    "专题五质量管理",
    "专题六资源管理",
    "专题七沟通、干系人管理",
    "专题八风险管理",
    "专题九采购管理",
    "专题十配置管理和变更管理",
    "专题十一综合案例",
]

def clean_text(text):
    """清理OCR文本中的常见错误"""
    # 页码标记移除
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    # 页眉页脚移除
    text = re.sub(r'高项案例分析.*羽仪老师', '', text)
    text = re.sub(r'软考（高项/中项/信管/监理等）/学历/入户', '', text)
    text = re.sub(r'软考羽仪老师', '', text)
    text = re.sub(r'如遇二道贩子缺课可加qq群：\d+购买', '', text)
    # 清理多余空行
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def split_document():
    """拆分文档"""
    # 创建输出目录
    os.makedirs(TITLE_OUTPUT_DIR, exist_ok=True)
    os.makedirs(ANSWER_OUTPUT_DIR, exist_ok=True)

    # 读取原文档
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 按页码标记分割
    pages = re.split(r'## 第 \d+ 页', content)

    # 第一部分：答题技巧（第2-4页，索引1-3）
    tips_content = ""
    for i in range(1, 4):  # 第2、3、4页
        if i < len(pages):
            tips_content += pages[i]

    # 保存答题技巧
    tips_content = clean_text(tips_content)
    tips_file = f"{TITLE_OUTPUT_DIR}/第一篇答题技巧.md"
    with open(tips_file, 'w', encoding='utf-8') as f:
        f.write("# 第一篇 答题技巧\n\n")
        f.write(tips_content)
    print(f"已保存: {tips_file}")

    # 第二部分：专项训练题目（第5-53页）
    # 提取所有题目内容
    title_section = ""
    for i in range(4, min(54, len(pages))):  # 第5页到第53页
        if i < len(pages):
            title_section += pages[i]

    # 第三部分：参考答案（第54-83页）
    answer_section = ""
    for i in range(53, len(pages)):  # 第54页到最后
        if i < len(pages):
            answer_section += pages[i]

    # 按专题拆分题目
    for topic in TOPICS:
        # 在题目部分查找专题内容
        topic_pattern = re.escape(topic)
        # 查找专题开始位置
        topic_match = re.search(topic_pattern, title_section)
        if topic_match:
            # 找下一个专题的位置来确定边界
            next_topic_idx = TOPICS.index(topic) + 1
            if next_topic_idx < len(TOPICS):
                next_topic = TOPICS[next_topic_idx]
                next_pattern = re.escape(next_topic)
                end_match = re.search(next_pattern, title_section[topic_match.start():])
                if end_match:
                    topic_content = title_section[topic_match.start():topic_match.start() + end_match.start()]
                else:
                    topic_content = title_section[topic_match.start():]
            else:
                # 最后一个专题，取到结束
                topic_content = title_section[topic_match.start():]

            # 清理并保存题目
            topic_content = clean_text(topic_content)
            # 提取专题标题后的内容（去掉专题标题本身）
            topic_content = re.sub(rf'^{topic_pattern}[\.。\s]*', '', topic_content)

            # 按题目拆分（识别"题目一"、"题目二"等）
            title_file = f"{TITLE_OUTPUT_DIR}/{topic}.md"
            with open(title_file, 'w', encoding='utf-8') as f:
                f.write(f"# {topic}\n\n")
                f.write(topic_content)
            print(f"已保存题目: {title_file}")

    # 拆分答案部分
    # 答案格式：专题名称后跟着各题目的答案
    answer_topics = [
        "专题一整合管理",
        "专题二范围管理",
        "专题三进度管理",
        "专题四成本管理",
        "专题五质量管理",
        "专题六资源管理",
        "专题七干系人和沟通管理",  # 注意答案部分的标题可能略有不同
        "专题八风险管理",
        "专题九采购管理",
        "专题十配置管理",
        "专题十一综合案例",
    ]

    # 更灵活地查找答案
    for i, topic in enumerate(answer_topics):
        # 尝试多种匹配模式
        patterns = [
            re.escape(topic),
            re.escape(topic.replace("专题七干系人和沟通管理", "专题七沟通、干系人管理")),
            re.escape(topic.replace("专题十配置管理", "专题十配置管理和变更管理")),
        ]

        for pattern in patterns:
            match = re.search(pattern, answer_section)
            if match:
                # 找下一个专题边界
                if i + 1 < len(answer_topics):
                    next_patterns = [
                        re.escape(answer_topics[i+1]),
                        re.escape(answer_topics[i+1].replace("专题七干系人和沟通管理", "专题七沟通、干系人管理")),
                    ]
                    for next_pattern in next_patterns:
                        end_match = re.search(next_pattern, answer_section[match.start():])
                        if end_match:
                            answer_content = answer_section[match.start():match.start() + end_match.start()]
                            break
                    else:
                        answer_content = answer_section[match.start():]
                else:
                    answer_content = answer_section[match.start():]

                # 清理并保存
                answer_content = clean_text(answer_content)
                # 使用标准专题名称作为文件名
                std_topic_name = TOPICS[i] if i < len(TOPICS) else topic
                answer_file = f"{ANSWER_OUTPUT_DIR}/{std_topic_name}.md"
                with open(answer_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {std_topic_name}\n\n")
                    f.write(answer_content)
                print(f"已保存答案: {answer_file}")
                break

def main():
    print("=" * 50)
    print("案例专题文档拆分脚本")
    print("=" * 50)
    print(f"输入文件: {INPUT_FILE}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()

    if not os.path.exists(INPUT_FILE):
        print(f"错误：输入文件不存在: {INPUT_FILE}")
        return

    split_document()

    print()
    print("=" * 50)
    print("拆分完成！")
    print("=" * 50)
    print(f"题目目录: {TITLE_OUTPUT_DIR}")
    print(f"答案目录: {ANSWER_OUTPUT_DIR}")

if __name__ == "__main__":
    main()