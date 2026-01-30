import os
from datetime import datetime
from openai import OpenAI

def run(project_name):
    """
    读取周边信息文档，使用硅基流动API生成总结，保存到processed_data目录。
    
    Args:
        project_name (str): 项目名称。
    
    Returns:
        dict: {"status": "success/error", "message": "..."}
    """
    api_key = "sk-ykloduxdazjstefqarmswtetrtafvvalaxtkqhxeldvsogtt"
    model = "deepseek-ai/DeepSeek-R1"
    timestamp = datetime.now().strftime("%Y%m%d")
    input_file = f"resources/working_data/{project_name}_{timestamp}/{project_name}_周边信息.txt"
    output_dir = f"resources/working_data/{project_name}_{timestamp}/processed_data"
    output_file = f"{output_dir}/{project_name}_llm_周边信息.txt"

    os.makedirs(output_dir, exist_ok=True)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"成功读取输入文件：{input_file}")
    except FileNotFoundError:
        print(f"错误：文件 {input_file} 未找到。")
        return {"status": "error", "message": f"文件 {input_file} 未找到"}
    except Exception as e:
        print(f"读取文件出错：{e}")
        return {"status": "error", "message": f"读取文件出错：{e}"}

    prompt = f"""
    请基于以下小区周边信息报告，对项目的周边配套进行全面总结。总结包括以下方面：
    1. 地段交通：步行便捷度、地铁/公交情况。
    2. 附近学校：学前/小学/初中数量和距离。
    3. 居住品质：绿化、舒适度、物业等。
    4. 生活配套：商业、医疗、餐饮、银行等。
    总结要简洁、专业，用中文输出，结构清晰，使用 bullet points 或小标题组织内容。
    
    原报告内容：
    {content}
    """

    client = OpenAI(base_url="https://api.siliconflow.cn/v1", api_key=api_key)

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        summary = response.choices[0].message.content.strip()
        print("API调用成功，生成的总结：")
        print(summary)
    except Exception as e:
        print(f"API调用出错：{e}")
        return {"status": "error", "message": f"API调用出错：{e}"}

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"项目名称：{project_name}\n")
            f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("周边配套信息总结：\n")
            f.write(summary)
        print(f"总结已保存到：{output_file}")
        return {"status": "success", "message": f"周边信息总结已保存到 {output_file}"}
    except Exception as e:
        print(f"保存文件出错：{e}")
        return {"status": "error", "message": f"保存文件出错：{e}"}