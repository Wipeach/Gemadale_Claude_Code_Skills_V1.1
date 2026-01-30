
from dotenv import load_dotenv
import os
import time
import shutil
import zipfile
from pathlib import Path, PurePosixPath
import requests

load_dotenv()

#文件批量上传
def File_batch_upload_analysis(token,files,file_path):
    url = "https://mineru.net/api/v4/file-urls/batch"
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "files": files,
        "model_version":"vlm"
    }
    file_path = file_path

    try:
        response = requests.post(url,headers=header,json=data)
        if response.status_code == 200:
            result = response.json()
            print('response success. result:{}'.format(result))
            if result["code"] == 0:
                batch_id = result["data"]["batch_id"]
                urls = result["data"]["file_urls"]
                print('batch_id:{},urls:{}'.format(batch_id, urls))
                for i in range(0, len(urls)):
                    with open(file_path[i], 'rb') as f:
                        res_upload = requests.put(urls[i], data=f)
                        if res_upload.status_code == 200:
                            print(f"{urls[i]} upload success")
                        else:
                            print(f"{urls[i]} upload failed")
                else:
                    return batch_id
            else:
                print('apply upload url failed,reason:{}'.format(result.msg))
        else:
            print('response not success. status:{} ,result:{}'.format(response.status_code, response))
    except Exception as err:
        print(err)

# 批量查询任务结果
def Batch_query_task_results(token,batch_id,max_retries=100, delay_seconds=3):
    for attempt in range(max_retries):
        print(f"第 {attempt + 1} 次查询...")
        url = f"https://mineru.net/api/v4/extract-results/batch/{batch_id}"
        header = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        res = requests.get(url, headers=header)
        res=res.json()
        if res.get("code") != 0:
            print(f"API调用失败: {res.get('msg')}")
            return None

        state=[i.get("state","error") for i in  res["data"]["extract_result"]]
        state_result=all(item == 'done' for item in state)
        if state_result:
            urls=[i.get("full_zip_url","") for i in  res["data"]["extract_result"]]
            urls_str='\n'.join(urls)
            print(f"上传成功，且转换完成，生成ZIP链接\nMinerU_Obtain_taskresult:\n{urls_str}")
            return urls
        else:
            print("上传成功，但还在转化...")
            time.sleep(delay_seconds)

    print(f"达到最大重试次数 {max_retries}，仍未获取到URL和token")
    return None

def download_file(url: str, dst_path: Path, timeout=60, chunk_size=1024 * 1024, max_retries=3) -> Path:
    """
    流式下载到 dst_path（自动创建目录），简单重试。
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
            print(f"[download] 第 {attempt}/{max_retries} 次失败: {e}")
            time.sleep(1.5 * attempt)

    raise RuntimeError(f"下载失败: {url}\n最后错误: {last_err}")

def extract_fullmd_and_images(zip_path: Path, out_dir: Path):
    """
    只提取 full.md 和 image/images 目录下的文件到 out_dir。
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

            # 目标落盘相对路径：
            # - full.md：固定写到 out_dir/full.md
            # - image/images：从 image/images 开始保留后续层级（image/xxx.png）
            if is_full_md:
                rel = Path("full.md")
            else:
                rel = Path(*p.parts[img_idx:])  # 保留 image/... 或 images/...

            target = out_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)

            # 直接从 zip 流式写出
            with z.open(member, "r") as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)

    return out_dir

def download_and_extract_mineru(zip_url: str, pdf_filename: str, save_root: str, url_cache: dict | None = None):
    """
    根据 pdf_filename 建立目录：save_root/<pdf_stem>/，并只提取 full.md + image/images。
    - url_cache 用于避免同一个 zip_url 重复下载
    """
    save_root = Path(save_root)
    pdf_stem = Path(pdf_filename).stem
    out_dir = save_root / pdf_stem

    url_cache = url_cache if url_cache is not None else {}

    # 1) 下载 zip（如已下载过则复用）
    if zip_url in url_cache and url_cache[zip_url].exists():
        zip_path = url_cache[zip_url]
    else:
        zip_path = save_root / "_zip_cache" / f"{pdf_stem}.zip"
        zip_path = download_file(zip_url, zip_path)
        url_cache[zip_url] = zip_path

    # 2) 解压指定内容
    extract_fullmd_and_images(zip_path, out_dir)
    print(f"[ok] 已输出: {out_dir}")
    return str(out_dir)

def download_results_for_batch(files: list, zip_urls: list, save_root: str):
    """
    假设 files 和 zip_urls 顺序一致（你当前代码就是这样拿的）。
    """
    cache = {}
    for meta, zip_url in zip(files, zip_urls):
        pdf_name = meta["name"]
        download_and_extract_mineru(zip_url, pdf_name, save_root, url_cache=cache)

if __name__ == '__main__':
    token = "eyJ0eXBlIjoiSldUIiwiYWxnIjoiSFM1MTIifQ.eyJqdGkiOiI4MjEwMDQ5OSIsInJvbCI6IlJPTEVfUkVHSVNURVIiLCJpc3MiOiJPcGVuWExhYiIsImlhdCI6MTc2OTQ5NDI2MSwiY2xpZW50SWQiOiJsa3pkeDU3bnZ5MjJqa3BxOXgydyIsInBob25lIjoiIiwib3BlbklkIjpudWxsLCJ1dWlkIjoiNjhiMjNkMDgtMDQ1Yy00MzkyLWFiMTAtYjA5NjI5NjM2MzBlIiwiZW1haWwiOiI1MzA4ODA5NjVAcXEuY29tIiwiZXhwIjoxNzcwNzAzODYxfQ.3DQ_EHz0-8Go_0XXuu72pXe8-NlCwIjSINZY5YeZ1P3fmaAbKdhO2NQag9e4TlfoFZuQEv1YI_kXv0Yd3V6pwQ"
    # token=os.getenv("MINERU_TOKEN")
    files=[ {"name":"T1.pdf", "data_id": "T1"},{"name":"T2.pdf", "data_id": "T2"},{"name":"T3.pdf", "data_id": "T3"}]
    file_path=["D:\Pycharm\Python_Project\PythonCrawlerPractice\PythonCrawlerPractice\金地集团\MinerU\T1.pdf",
               "D:\Pycharm\Python_Project\PythonCrawlerPractice\PythonCrawlerPractice\金地集团\MinerU\T2.pdf",
               "D:\Pycharm\Python_Project\PythonCrawlerPractice\PythonCrawlerPractice\金地集团\MinerU\T3.pdf"]
    batch_id=File_batch_upload_analysis(token,files,file_path)
    urls = Batch_query_task_results(token,batch_id)

    save_root = r"D:\Pycharm\Python_Project\PythonCrawlerPractice\PythonCrawlerPractice\金地集团\MinerU\outputs"
    download_results_for_batch(files, urls, save_root)





