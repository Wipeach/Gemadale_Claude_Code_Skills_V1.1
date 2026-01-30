---
name: minerU
description: MinerU 文档解析服务 - 将 PDF、PPT、图片等文档转换为 Markdown 格式，支持 OCR 公式识别，自动下载并解压到本地文件夹
version: 1.0.0
author: 金地上海公司·投资部
tags: [pdf, parser, ocr, markdown, document-conversion]
---

# MinerU 文档解析服务

## 概述

MinerU 是一个强大的文档解析 API 服务，支持将多种格式的文档（PDF、PPT、PPTX、图片等）转换为结构化的 Markdown 格式。本技能提供了完整的 Python 封装，包括：

- **自动上传**：支持本地文件直接上传到 MinerU 服务器
- **智能轮询**：自动等待任务完成，无需手动查询
- **一键提取**：自动下载 ZIP 并提取 `full.md` 和 `images/` 文件夹
- **批量处理**：支持批量解析多个文档

## 功能特点

- ✅ **支持多种格式**：PDF、PPT、PPTX、图片等
- ✅ **OCR 文字识别**：可识别扫描件和图片中的文字
- ✅ **公式识别**：支持数学公式的解析（LaTeX 格式）
- ✅ **表格识别**：自动将表格转换为 HTML 格式
- ✅ **结构化输出**：生成清晰的 Markdown 层级结构
- ✅ **图片提取**：自动提取文档中的所有图片

## 快速开始

### 方式一：通过 Skill Tool 调用（推荐）

直接在对话中请求解析文档：

```
请使用 minerU 解析这个 PDF：Test_result/document.pdf
```

或者指定输出目录：

```
使用 minerU 解析 Test_result/document.pdf，输出到 Test_result/output
```

### 方式二：命令行调用

```bash
# 进入技能目录
cd skills/minerU

# 解析单个文档
python scripts/parse.py path/to/document.pdf

# 指定输出目录
python scripts/parse.py path/to/document.pdf -o path/to/output

# 使用自定义 Token
python scripts/parse.py path/to/document.pdf --token YOUR_TOKEN
```

### 方式三：作为 Python 库使用

```python
from skills.minerU.minerU import MinerUClient

# 初始化客户端
client = MinerUClient()

# 解析单个文档
result = client.parse_and_extract(
    pdf_path="path/to/document.pdf",
    save_root="path/to/output"
)

print(f"结果已保存到: {result}")
# 输出: path/to/output/document/full.md 和 path/to/output/document/images/
```

## 配置

### API Token

MinerU 需要 API Token 才能使用。将 Token 设置为环境变量：

```bash
# 在 skills/minerU/.env 文件中设置
MINERU_TOKEN=your_token_here
```

或者在代码中直接传入：

```python
client = MinerUClient(token="your_token_here")
```

## 使用示例

### 单个文档解析

```python
from skills.minerU.minerU import MinerUClient

client = MinerUClient()

# 解析 PDF
result = client.parse_and_extract(
    pdf_path="investment_report.pdf",
    save_root="./Test_result"
)

# 查看结果
print(f"full.md: {result}/full.md")
print(f"images: {result}/images/")
```

### 批量解析

```python
from skills.minerU.minerU import MinerUClient

client = MinerUClient()

# 批量上传
files = [
    {"name": "report1.pdf", "data_id": "report1"},
    {"name": "report2.pdf", "data_id": "report2"}
]
file_paths = ["path/to/report1.pdf", "path/to/report2.pdf"]

batch_id = client.batch_upload(files, file_paths)

# 批量下载
results = client.batch_download(
    files=files,
    batch_id=batch_id,
    save_root="./Test_result"
)

for result in results:
    print(f"解析完成: {result}")
```

### 处理整个目录

```python
from skills.minerU.minerU import MinerUClient

client = MinerUClient()

# 处理目录中的所有 PDF
results = client.process_directory(
    pdf_dir="./Test_result/pdfs",
    save_root="./Test_result/parsed"
)

print(f"共处理 {len(results)} 个文件")
```

## 输出格式

解析后的目录结构：

```
output/
└── document_name/
    ├── full.md          # 完整的 Markdown 内容
    └── images/          # 提取的图片文件夹
        ├── image1.jpg
        ├── image2.png
        └── ...
```

### full.md 内容示例

```markdown
# 文档标题

# 第一章

内容段落...

![图片描述](images/image1.jpg)

| 列1 | 列2 |
|-----|-----|
| 数据 | 数据 |
```

## API 参数说明

### MinerUClient 初始化

```python
client = MinerUClient(token=None)
```

- `token`（可选）：MinerU API Token。如为 None，则从环境变量 `MINERU_TOKEN` 读取

### parse_and_extract - 单文件解析

```python
result = client.parse_and_extract(
    pdf_path: str,           # PDF/PPT 文件路径
    save_root: str,          # 输出根目录
    max_retries: int = 100,  # 最大轮询次数
    delay_seconds: int = 3   # 轮询间隔（秒）
)
```

**返回值**：输出目录的完整路径

### batch_upload - 批量上传

```python
batch_id = client.batch_upload(
    files: List[Dict],       # 文件元数据列表
    file_paths: List[str]    # 文件路径列表
)
```

**返回值**：批处理任务 ID

### batch_download - 批量下载

```python
results = client.batch_download(
    files: List[Dict],       # 文件元数据列表
    batch_id: str,           # 批处理任务 ID
    save_root: str,          # 输出根目录
    max_retries: int = 100,
    delay_seconds: int = 3
)
```

**返回值**：输出目录路径列表

## 故障排查

### Token 无效

```
错误: Token 未提供。请传入 token 或设置环境变量 MINERU_TOKEN
```

**解决方案**：
1. 检查 `skills/minerU/.env` 文件中的 `MINERU_TOKEN` 是否正确
2. 确认 Token 未过期

### 文件上传失败

```
错误: 上传失败
```

**解决方案**：
1. 检查网络连接
2. 确认文件路径正确
3. 检查文件大小（建议小于 50MB）

### 解析超时

```
达到最大重试次数，仍未完成
```

**解决方案**：
1. 增加 `max_retries` 参数值
2. 增加 `delay_seconds` 参数值
3. 检查 MinerU 服务状态

## 依赖安装

```bash
pip install requests python-dotenv
```

## 许可证

内部使用 - 金地上海公司·投资部

## 相关链接

- MinerU 官网: https://mineru.net/
- API 文档: https://mineru.net/docs
