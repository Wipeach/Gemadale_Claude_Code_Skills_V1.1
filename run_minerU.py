"""
MinerU PDF 解析脚本
将 PDF 上传到 MinerU 服务进行解析，提取 full.md 和 images 文件夹
"""

import sys
import os

# 添加 minerU skill 路径
sys.path.insert(0, r"D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\skills\minerU")

# 设置环境变量加载 .env 文件
from dotenv import load_dotenv
load_dotenv(r"D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\skills\minerU\.env")

from minerU import MinerUClient

def main():
    # PDF 文件路径
    pdf_path = r"Test_result\【投资分析报告-路演网页多模态】松江区泗泾04-08号地块.pdf"

    # 输出目录
    save_root = r"Test_result"

    print(f"开始解析 PDF:")
    print(f"  输入: {pdf_path}")
    print(f"  输出: {save_root}")
    print()

    try:
        # 初始化客户端（token 从环境变量 MINERU_TOKEN 读取）
        client = MinerUClient()

        # 解析 PDF 并提取结果
        output_dir = client.parse_and_extract(
            pdf_path=pdf_path,
            save_root=save_root,
            max_retries=100,  # 最大轮询次数
            delay_seconds=3   # 每次轮询间隔 3 秒
        )

        print()
        print(f"解析完成！")
        print(f"结果保存在: {output_dir}")
        print(f"  - {os.path.join(output_dir, 'full.md')}")
        print(f"  - {os.path.join(output_dir, 'images')}")

    except Exception as e:
        print(f"解析失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
