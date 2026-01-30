# MinerU Skill

MinerU 文档解析服务 - 将 PDF、PPT、图片等文档转换为 Markdown 格式，支持 OCR 公式识别，自动下载并解压到本地文件夹。

## 功能特性

- 批量上传 PDF 文件到 MinerU 服务器
- 自动轮询解析状态，等待任务完成
- 自动下载解析结果 ZIP 文件
- 智能提取 `full.md` 和 `images` 文件夹
- 支持 URL 缓存，避免重复下载
- 支持环境变量配置 Token

## 快速开始

### 1. 安装依赖

```bash
pip install requests python-dotenv
```

### 2. 配置 Token

复制 `.env.example` 为 `.env` 并填写你的 Token：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```
MINERU_TOKEN=your_actual_token_here
```

### 3. 使用

```python
from minerU import MinerUClient

client = MinerUClient()

# 解析单个 PDF
result = client.parse_and_extract(
    pdf_path="path/to/document.pdf",
    save_root="path/to/output"
)

print(f"结果保存在: {result}")
```

## 目录结构

```
skills/minerU/
├── SKILL.md          # 技能文档
├── README.md         # 本文件
├── minerU.py         # 核心客户端代码
├── example.py        # 使用示例
├── .env.example      # 环境变量模板
└── .env              # 环境变量配置（需自行创建）
```

## API 文档

详细的 API 文档请参阅 [SKILL.md](./SKILL.md)

## 使用示例

### 单文件解析

```python
from minerU import MinerUClient

client = MinerUClient()
output_dir = client.parse_and_extract("file.pdf", "output")
```

### 批量处理

```python
files = [
    {"name": "doc1.pdf", "data_id": "doc1"},
    {"name": "doc2.pdf", "data_id": "doc2"}
]
paths = ["path/to/doc1.pdf", "path/to/doc2.pdf"]

batch_id = client.batch_upload(files, paths)
results = client.batch_download(files, batch_id, "output")
```

### 目录处理

```python
results = client.process_directory(
    pdf_dir="path/to/pdfs",
    save_root="output"
)
```

## 输出结构

```
save_root/
├── document_name/
│   ├── full.md          # Markdown 解析结果
│   └── images/          # 提取的图片
│       ├── image_1.png
│       └── ...
└── _zip_cache/          # ZIP 缓存
    └── document_name.zip
```

## 注意事项

1. 确保 Token 有效且有足够的配额
2. 大文件解析可能需要较长时间
3. 建议使用绝对路径避免路径问题
4. Windows 路径使用 `r"path"` 或正斜杠

## License

Proprietary
