#!/usr/bin/env python3
"""
MinerU Skill - 主入口点

当通过 Skill tool 调用时，此文件作为执行入口。
支持从命令行参数接收 PDF 文件路径和输出目录。
"""

import sys
import os
from pathlib import Path

# 确保可以导入 minerU 模块
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from minerU import MinerUClient


def main():
    """
    主入口函数。

    参数格式：
        python -m minerU <pdf_path> [output_dir]

    或者通过 sys.argv 传递：
        sys.argv = ["minerU", "path/to/file.pdf", "path/to/output"]
    """
    # 解析参数
    if len(sys.argv) < 2:
        print("用法: python -m minerU <pdf_path> [output_dir]")
        print("示例: python -m minerU Test_result/document.pdf Test_result/output")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None

    print(f"=== MinerU 文档解析 ===")
    print(f"输入文件: {pdf_path}")
    print(f"输出目录: {output_dir or '默认'}")
    print()

    try:
        # 初始化客户端
        client = MinerUClient()

        # 解析文档
        result = client.parse_and_extract(
            pdf_path=pdf_path,
            save_root=output_dir or "./Test_result"
        )

        print(f"\n✓ 解析完成!")
        print(f"输出目录: {result}")

        # 统计结果
        result_path = Path(result)
        full_md = result_path / "full.md"
        images_dir = result_path / "images"

        if full_md.exists():
            print(f"  full.md: {full_md.stat().st_size / 1024:.1f} KB")

        if images_dir.exists():
            image_count = len(list(images_dir.glob("*")))
            print(f"  图片数量: {image_count}")

        return 0

    except FileNotFoundError as e:
        print(f"✗ 文件错误: {e}")
        return 1

    except Exception as e:
        print(f"✗ 解析失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
