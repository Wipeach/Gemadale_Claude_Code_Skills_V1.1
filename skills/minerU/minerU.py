"""
MinerU 文档解析服务客户端

将 PDF、PPT、图片等文档上传至 MinerU 服务器解析，支持 OCR 公式识别，
自动下载并解压提取 full.md 和 images 文件夹。
"""

import os
import time
import shutil
import zipfile
from pathlib import Path, PurePosixPath
from typing import Optional, List, Dict, Any
import requests

from dotenv import load_dotenv

load_dotenv()


class MinerUClient:
    """MinerU 文档解析服务客户端"""

    BASE_URL = "https://mineru.net/api/v4"

    def __init__(self, token: Optional[str] = None):
        """
        初始化客户端

        Args:
            token: MinerU API Token。如为 None，则从环境变量 MINERU_TOKEN 读取
        """
        self.token = token or os.getenv("MINERU_TOKEN")
        if not self.token:
            raise ValueError(
                "Token 未提供。请传入 token 或设置环境变量 MINERU_TOKEN"
            )

    def _batch_upload_analysis(
        self, files: List[Dict[str, str]], file_path: List[str]
    ) -> Optional[str]:
        """
        批量上传文件到 MinerU 服务器

        Args:
            files: 文件元数据列表，格式: [{"name": "file.pdf", "data_id": "id"}, ...]
            file_path: PDF 文件路径列表

        Returns:
            batch_id: 批处理任务 ID，失败返回 None
        """
        url = f"{self.BASE_URL}/file-urls/batch"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        data = {"files": files, "model_version": "vlm"}

        try:
            response = requests.post(url, headers=header, json=data)
            if response.status_code == 200:
                result = response.json()
                if result.get("code") == 0:
                    batch_id = result["data"]["batch_id"]
                    urls = result["data"]["file_urls"]

                    # 上传文件到返回的 URLs
                    for i, url in enumerate(urls):
                        with open(file_path[i], "rb") as f:
                            res_upload = requests.put(url, data=f)
                            if res_upload.status_code == 200:
                                print(f"{file_path[i]} 上传成功")
                            else:
                                print(f"{file_path[i]} 上传失败")
                    return batch_id
                else:
                    print(f"获取上传 URL 失败: {result.get('msg')}")
            else:
                print(f"API 请求失败: {response.status_code}")
        except Exception as err:
            print(f"上传异常: {err}")

        return None

    def _batch_query_results(
        self,
        batch_id: str,
        max_retries: int = 100,
        delay_seconds: int = 3
    ) -> Optional[List[str]]:
        """
        批量查询任务结果

        Args:
            batch_id: 批处理任务 ID
            max_retries: 最大轮询次数
            delay_seconds: 每次轮询间隔（秒）

        Returns:
            ZIP 文件 URL 列表，失败返回 None
        """
        for attempt in range(max_retries):
            print(f"第 {attempt + 1} 次查询...")
            url = f"{self.BASE_URL}/extract-results/batch/{batch_id}"
            header = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }

            try:
                res = requests.get(url, headers=header)
                res = res.json()

                if res.get("code") != 0:
                    print(f"API 调用失败: {res.get('msg')}")
                    return None

                states = [
                    item.get("state", "error")
                    for item in res["data"]["extract_result"]
                ]
                all_done = all(item == "done" for item in states)

                if all_done:
                    urls = [
                        item.get("full_zip_url", "")
                        for item in res["data"]["extract_result"]
                    ]
                    print("解析完成！")
                    return urls
                else:
                    print("还在解析中...")
                    time.sleep(delay_seconds)
            except Exception as err:
                print(f"查询异常: {err}")
                time.sleep(delay_seconds)

        print(f"达到最大重试次数 {max_retries}，仍未完成")
        return None

    @staticmethod
    def _download_file(
        url: str,
        dst_path: Path,
        timeout: int = 60,
        chunk_size: int = 1024 * 1024,
        max_retries: int = 3
    ) -> Path:
        """
        流式下载文件到 dst_path（自动创建目录），支持重试

        Args:
            url: 下载 URL
            dst_path: 目标路径
            timeout: 超时时间（秒）
            chunk_size: 分块大小
            max_retries: 最大重试次数

        Returns:
            下载文件的路径
        """
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        last_err = None
        for attempt in range(1, max_retries + 1):
            try:
                with requests.get(url, stream=True, timeout=timeout) as r:
                    r.raise_for_status()
                    tmp_path = dst_path.with_suffix(dst_path.suffix + ".part")
                    with open(tmp_path, "wb") as f:
                        for chunk in r.iter_content(chunk_size=chunk_size):
                            if chunk:
                                f.write(chunk)
                    tmp_path.replace(dst_path)
                return dst_path
            except Exception as e:
                last_err = e
                print(f"下载第 {attempt}/{max_retries} 次失败: {e}")
                time.sleep(1.5 * attempt)

        raise RuntimeError(f"下载失败: {url}\n最后错误: {last_err}")

    @staticmethod
    def _extract_fullmd_and_images(zip_path: Path, out_dir: Path) -> Path:
        """
        只提取 full.md 和 image/images 目录下的文件到 out_dir

        Args:
            zip_path: ZIP 文件路径
            out_dir: 输出目录

        Returns:
            输出目录路径
        """
        out_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.infolist():
                # 跳过目录
                if member.is_dir():
                    continue

                # ZIP 内部路径统一用 posix 处理
                p = PurePosixPath(member.filename)

                # 规则1：full.md
                is_full_md = (p.name.lower() == "full.md")

                # 规则2：image 或 images 目录段
                parts_lower = [x.lower() for x in p.parts]
                img_idx = None
                for key in ("image", "images"):
                    if key in parts_lower:
                        img_idx = parts_lower.index(key)
                        break
                is_image_file = (img_idx is not None)

                if not (is_full_md or is_image_file):
                    continue

                # 目标落盘相对路径
                if is_full_md:
                    rel = Path("full.md")
                else:
                    rel = Path(*p.parts[img_idx:])

                target = out_dir / rel
                target.parent.mkdir(parents=True, exist_ok=True)

                # 直接从 zip 流式写出
                with z.open(member, "r") as src, open(target, "wb") as dst:
                    shutil.copyfileobj(src, dst)

        return out_dir

    def _download_and_extract(
        self,
        zip_url: str,
        pdf_filename: str,
        save_root: str,
        url_cache: Optional[Dict[str, Path]] = None
    ) -> str:
        """
        下载 ZIP 并提取 full.md + image/images

        Args:
            zip_url: ZIP 文件下载 URL
            pdf_filename: PDF 文件名（用于命名输出目录）
            save_root: 结果保存根目录
            url_cache: URL 缓存字典，避免重复下载

        Returns:
            输出目录路径
        """
        save_root = Path(save_root)
        pdf_stem = Path(pdf_filename).stem
        out_dir = save_root / pdf_stem

        url_cache = url_cache if url_cache is not None else {}

        # 下载 zip（如已下载过则复用）
        if zip_url in url_cache and url_cache[zip_url].exists():
            zip_path = url_cache[zip_url]
        else:
            zip_path = save_root / "_zip_cache" / f"{pdf_stem}.zip"
            zip_path = self._download_file(zip_url, zip_path)
            url_cache[zip_url] = zip_path

        # 解压指定内容
        self._extract_fullmd_and_images(zip_path, out_dir)
        print(f"[完成] 已输出: {out_dir}")
        return str(out_dir)

    def parse_and_extract(
        self,
        pdf_path: str,
        save_root: str,
        max_retries: int = 100,
        delay_seconds: int = 3
    ) -> str:
        """
        解析单个 PDF 并提取结果

        Args:
            pdf_path: PDF 文件路径
            save_root: 结果保存根目录
            max_retries: 最大轮询次数
            delay_seconds: 每次轮询间隔（秒）

        Returns:
            输出目录路径
        """
        pdf_name = Path(pdf_path).name
        pdf_stem = Path(pdf_path).stem

        files = [{"name": pdf_name, "data_id": pdf_stem}]
        file_paths = [pdf_path]

        # 上传
        print(f"正在上传: {pdf_path}")
        batch_id = self._batch_upload_analysis(files, file_paths)
        if not batch_id:
            raise RuntimeError("上传失败")

        # 查询结果
        print("等待解析完成...")
        urls = self._batch_query_results(batch_id, max_retries, delay_seconds)
        if not urls or not urls[0]:
            raise RuntimeError("解析超时或失败")

        # 下载并提取
        return self._download_and_extract(urls[0], pdf_name, save_root)

    def batch_upload(
        self,
        files: List[Dict[str, str]],
        file_paths: List[str]
    ) -> Optional[str]:
        """
        批量上传 PDF 文件

        Args:
            files: 文件元数据列表
            file_paths: PDF 文件路径列表

        Returns:
            batch_id: 批处理任务 ID
        """
        return self._batch_upload_analysis(files, file_paths)

    def batch_download(
        self,
        files: List[Dict[str, str]],
        batch_id: str,
        save_root: str,
        max_retries: int = 100,
        delay_seconds: int = 3
    ) -> List[str]:
        """
        批量下载并提取结果

        Args:
            files: 文件元数据列表
            batch_id: 批处理任务 ID
            save_root: 结果保存根目录
            max_retries: 最大轮询次数
            delay_seconds: 每次轮询间隔（秒）

        Returns:
            输出目录路径列表
        """
        urls = self._batch_query_results(batch_id, max_retries, delay_seconds)
        if not urls:
            raise RuntimeError("获取下载链接失败")

        cache = {}
        results = []
        for meta, zip_url in zip(files, urls):
            pdf_name = meta["name"]
            result = self._download_and_extract(zip_url, pdf_name, save_root, cache)
            results.append(result)

        return results

    def process_directory(
        self,
        pdf_dir: str,
        save_root: str
    ) -> List[str]:
        """
        处理整个目录的 PDF 文件

        Args:
            pdf_dir: PDF 文件目录
            save_root: 结果保存根目录

        Returns:
            所有输出目录路径列表
        """
        pdf_dir = Path(pdf_dir)
        pdf_files = list(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            print(f"目录中没有 PDF 文件: {pdf_dir}")
            return []

        files = []
        file_paths = []

        for pdf_path in pdf_files:
            pdf_stem = pdf_path.stem
            files.append({"name": pdf_path.name, "data_id": pdf_stem})
            file_paths.append(str(pdf_path))

        batch_id = self.batch_upload(files, file_paths)
        if not batch_id:
            raise RuntimeError("批量上传失败")

        return self.batch_download(files, batch_id, save_root)
