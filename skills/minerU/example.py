"""
MinerU 使用示例

演示如何使用 MinerU 客户端解析 PDF 文件
"""

import os
from minerU import MinerUClient

# 配置 Token（建议使用环境变量）
# 在 .env 文件中设置: MINERU_TOKEN=your_token_here
TOKEN = os.getenv("MINERU_TOKEN", "your_token_here")


def example_single_file():
    """示例：解析单个 PDF 文件"""
    print("=" * 50)
    print("示例 1: 解析单个 PDF 文件")
    print("=" * 50)

    client = MinerUClient(token=TOKEN)

    result = client.parse_and_extract(
        pdf_path="D:/documents/example.pdf",  # 修改为你的 PDF 路径
        save_root="D:/outputs"
    )

    print(f"\n解析完成！结果保存在: {result}")
    print(f"- Markdown 文件: {result}/full.md")
    print(f"- 图片文件夹: {result}/images/")


def example_batch_files():
    """示例：批量解析多个 PDF 文件"""
    print("\n" + "=" * 50)
    print("示例 2: 批量解析多个 PDF 文件")
    print("=" * 50)

    client = MinerUClient(token=TOKEN)

    # 定义文件信息
    files = [
        {"name": "document1.pdf", "data_id": "doc1"},
        {"name": "document2.pdf", "data_id": "doc2"},
        {"name": "document3.pdf", "data_id": "doc3"}
    ]
    file_paths = [
        "D:/documents/document1.pdf",  # 修改为实际路径
        "D:/documents/document2.pdf",
        "D:/documents/document3.pdf"
    ]

    # 批量上传
    print("正在批量上传...")
    batch_id = client.batch_upload(files, file_paths)

    # 批量下载
    print("等待解析完成...")
    results = client.batch_download(
        files=files,
        batch_id=batch_id,
        save_root="D:/outputs"
    )

    print(f"\n全部完成！共处理 {len(results)} 个文件")
    for i, result in enumerate(results):
        print(f"{i+1}. {result}")


def example_directory():
    """示例：处理整个目录的 PDF 文件"""
    print("\n" + "=" * 50)
    print("示例 3: 处理整个目录")
    print("=" * 50)

    client = MinerUClient(token=TOKEN)

    results = client.process_directory(
        pdf_dir="D:/documents/pdfs",  # 修改为你的 PDF 目录
        save_root="D:/outputs"
    )

    print(f"\n目录处理完成！共处理 {len(results)} 个文件")
    for result in results:
        print(f"- {result}")


def example_read_result():
    """示例：读取解析结果"""
    print("\n" + "=" * 50)
    print("示例 4: 读取解析结果")
    print("=" * 50)

    output_dir = "D:/outputs/document"

    # 读取 full.md
    md_path = f"{output_dir}/full.md"
    if os.path.exists(md_path):
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
            print(f"Markdown 内容预览（前500字）:\n")
            print(content[:500])
            print("..." if len(content) > 500 else "")
    else:
        print(f"文件不存在: {md_path}")

    # 列出图片文件
    images_dir = f"{output_dir}/images"
    if os.path.exists(images_dir):
        images = os.listdir(images_dir)
        print(f"\n提取的图片文件 ({len(images)} 个):")
        for img in images[:10]:  # 只显示前10个
            print(f"  - {img}")
        if len(images) > 10:
            print(f"  ... 还有 {len(images) - 10} 个文件")


if __name__ == "__main__":
    # 运行示例
    # example_single_file()
    # example_batch_files()
    # example_directory()
    example_read_result()
