# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指导。

## 项目概述

软考学习资料仓库，目标是将扫描版PDF解析为结构化Markdown，构建学习系统。当前目标是先攻克选择题。

## 关键目录

```
辅导资料/           # PDF学习资料
  ├── 02：章节演练-cp.pdf           # 章节练习题
  └── 06：高项章节练习参考答案.pdf   # 参考答案
output/             # 解析后的Markdown文件
  ├── 章节演练/     # 题目文件（按章节分类）
  └── 参考答案/     # 答案文件（按章节分类）
备考进度.md         # 学习进度跟踪（错题记录、知识点总结）
```

## PDF处理架构

### 处理流程

```
扫描版PDF → 图像预处理 → OCR识别 → 文本修正 → 格式化 → Markdown输出
             ↓
      对比度增强
      锐化处理
      放大3倍
```

### 核心脚本

| 脚本 | 用途 | 输入 | 输出 |
|------|------|------|------|
| `process_full_pdf.py` | 处理章节演练PDF | 章节演练PDF | `output/章节演练/*.md` |
| `process_answers.py` | 处理参考答案PDF | 参考答案PDF | `output/参考答案/*.md` |
| `fix_chapters_v2.py` | 修复格式、检测不完整题目 | 章节Markdown | 修正后的Markdown |
| `fix_missing_options.py` | 标记跨页丢失的选项 | 章节Markdown | 添加缺失标记 |
| `check_chapters.py` | 校对题目与答案 | 题目+答案Markdown | 校对报告 |

### 关键函数

**图像预处理** (`preprocess_image`):
- 对比度增强 1.5倍
- 锐化处理
- 放大 3 倍提高 OCR 精度

**OCR修正** (`OCR_CORRECTIONS` 字典在 `process_full_pdf.py` 和 `process_answers.py`):
- 修正常见OCR错误（如 `laaS` → `IaaS`、`数字李生` → `数字孪生`）
- 修正选项格式（全角→半角，如 `A．` → `A.`）
- 圆圈数字修正（如 `236` → `②③⑥`）
- 添加新修正规则时需同时更新两个脚本

**章节检测** (`is_chapter_title`):
- 匹配模式：`第[一二三四五六七八九十百]+章` 或 `第\d+章`
- 自动按章节分文件保存

**章节名称映射** (`CHAPTER_MAP` 在 `check_chapters.py`):
- 定义题目文件名到答案文件名的映射
- 题目文件名有空格（如 `第一章 信息化发展.md`）
- 答案文件名无空格（如 `第一章信息化发展.md`）

### 进度恢复机制

- 进度保存在 `output/*/progress.json`
- 每10页自动保存进度
- 中断后从 `last_page` 继续处理

## 常用命令

### 依赖安装
```bash
pip install pymupdf rapidocr-onnxruntime pillow
```

### 完整处理流程
```bash
# 1. 处理题目PDF（首次运行或修改PDF_PATH）
python process_full_pdf.py

# 2. 处理参考答案PDF
python process_answers.py

# 3. 修复格式并检测问题
python fix_chapters_v2.py

# 4. 标记缺失选项
python fix_missing_options.py

# 5. 校对题目与答案
python check_chapters.py
```

### 配置修改

脚本路径为硬编码，处理不同PDF需修改：
- `PDF_PATH` - 输入PDF路径
- `OUTPUT_DIR` - 输出目录路径
- `SCALE` - 图片放大倍数（默认3倍）

### 备选解析器
```bash
magic-pdf --path "辅导资料/xxx.pdf" --output-dir output/
```

### OCR测试脚本

测试不同OCR引擎效果：
```bash
python test_ocr_v3.py      # RapidOCR测试（推荐）
python test_paddleocr.py   # PaddleOCR测试
```

测试结果输出到 `test_output/` 目录。

## 输出格式

**题目格式**:
```markdown
**1、题干内容**
  A. 选项A
  B. 选项B
  C. 选项C
  D. 选项D
```

**答案格式**:
```markdown
**1、【答案】A**
**1、【解析】...**
```

## 已知问题

1. **跨页题目丢失选项** - 标记为 `【需补充：跨页丢失】`，需对照原PDF补充
2. **OCR识别错误** - 通过 `OCR_CORRECTIONS` 字典修正常见错误
3. **章节标题重复** - `fix_chapters_v2.py` 自动处理

## 学习进度管理

`备考进度.md` 跟踪：
- 各章节完成情况和正确率
- 错题记录及错误原因分析
- 知识点薄弱项
- 学习笔记（核心知识点总结）

## 故障排除

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| OCR识别错误多 | 扫描件质量差 | 调整 `SCALE` 值（默认3）或增强预处理参数 |
| 处理中断 | 内存不足或异常 | 检查 `progress.json`，从 `last_page` 继续 |
| 章节未分割 | 章节标题匹配失败 | 检查 `CHAPTER_PATTERNS`，添加新模式 |
| 答案对不上 | 文件名映射错误 | 更新 `check_chapters.py` 中的 `CHAPTER_MAP` |
| 选项缺失 | 跨页断裂 | 运行 `fix_missing_options.py` 标记后人工补充 |

### 重新处理特定章节

若需重新处理某章节：
1. 删除对应的 `.md` 文件
2. 修改 `progress.json` 中的 `last_page` 为该章节起始页
3. 重新运行处理脚本