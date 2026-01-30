#!/usr/bin/env python3
"""
MinerU PDF Parser - 可执行脚本

通过命令行调用 MinerU 服务解析 PDF/PPT/图片文档。
支持单文件解析，自动下载并提取 full.md 和 images 文件夹。
"""

import os
import sys
import argparse
from pathlib import Path

# 添加父目录到路径，以便导入 minerU 模块
script_dir = Path(__file__).parent
skill_dir = script_dir.parent
sys.path.insert(0, str(skill_dir))

from minerU import MinerUClient


def parse_document(
    file_path: str,
    output_dir: str = None,
    token: str = None,
    max_retries: int = 100,
    delay_seconds: int = 3
) -> str:
    """
    解析文档（PDF/PPT/图片）并提取结果

    Args:
        file_path: 输入文件路径
        output_dir: 输出目录（默认为当前目录下的 output）
        token: MinerU API Token（默认从环境变量读取）
        max_retries: 最大轮询次数
        delay_seconds: 轮询间隔秒数

    Returns:
        输出目录路径
    """
    file_path = Path(file_path).absolute()

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 默认输出目录
    if output_dir is None:
        output_dir = file_path.parent.parent / "output"

    output_dir = Path(output_dir).absolute()

    print(f"=== MinerU 文档解析 ===")
    print(f"输入文件: {file_path}")
    print(f"输出目录: {output_dir}")
    print(f"文件大小: {file_path.stat().st_size / 1024 / 1024:.2f} MB")
    print()

    # 初始化客户端
    if token:
        client = MinerUClient(token=token)
    else:
        client = MinerUClient()

    # 解析文档
    try:
        result = client.parse_and_extract(
            pdf_path=str(file_path),
            save_root=str(output_dir),
            max_retries=max_retries,
            delay_seconds=delay_seconds
        )

        print(f"\n=== 解析完成 ===")
        print(f"输出目录: {result}")

        # 统计结果
        result_path = Path(result)
        full_md = result_path / "full.md"
        images_dir = result_path / "images"

        if full_md.exists():
            print(f"full.md: {full_md.stat().st_size / 1024:.1f} KB")

        if images_dir.exists():
            image_count = len(list(images_dir.glob("*")))
            print(f"图片数量: {image_count}")

        return str(result)

    except Exception as e:
        print(f"\n错误: {e}", file=sys.stderr)
        raise


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="MinerU 文档解析服务 - 将 PDF/PPT/图片转换为 Markdown",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 解析单个 PDF
  python parse.py document.pdf

  # 指定输出目录
  python parse.py document.pdf -o ./output

  # 使用自定义 Token
  python parse.py document.pdf --token YOUR_TOKEN

  # 批量处理（使用通配符）
  python parse.py *.pdf -o ./output
        """
    )

    parser.add_argument(
        "input",
        help="输入文件路径（PDF/PPT/图片）"
    )
    parser.add_argument(
        "-o", "--output",
        help="输出目录（默认为 ./output）",
        default=None
    )
    parser.add_argument(
        "-t", "--token",
        help="MinerU API Token（默认从环境变量 MINERU_TOKEN 读取）",
        default=None
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=100,
        help="最大轮询次数（默认: 100）"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=3,
        help="轮询间隔秒数（默认: 3）"
    )

    args = parser.parse_args()

    try:
        result = parse_document(
            file_path=args.input,
            output_dir=args.output,
            token=args.token,
            max_retries=args.max_retries,
            delay_seconds=args.delay
        )
        print(f"\n✓ 成功: {result}")
        return 0

    except FileNotFoundError as e:
        print(f"✗ 文件错误: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"✗ 解析失败: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
