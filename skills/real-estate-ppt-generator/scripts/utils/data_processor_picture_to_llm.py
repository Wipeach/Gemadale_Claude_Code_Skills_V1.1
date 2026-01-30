# -*- coding: utf-8 -*-
"""
Picture to LLM Data Processor
Analyzes floor plan images using SiliconFlow API to generate layout descriptions and analysis
"""

import os
import base64
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def run(project_name: str, image_paths: List[str] = None) -> Dict[str, Any]:
    """Run the floor plan analysis with a given project name and list of image paths."""
    
    # 设置默认图片路径列表
    if image_paths is None:
        image_paths = [
            "resources/images/room_style1.jpg",  # 高层住宅1
            "resources/images/room_style2.jpg",  # 高层住宅2
            "resources/images/room_style3.jpg",  # 高层住宅3
            "resources/images/room_style4.jpg",  # 叠拼1
            "resources/images/room_style5.jpg"   # 叠拼2
        ]
    
    # 设置SiliconFlow API客户端
    # 注意：API密钥应通过环境变量或配置文件提供，此处仅保留占位符
    client = OpenAI(
        api_key=os.getenv("SILICONFLOW_API_KEY", "sk-ykloduxdazjstefqarmswtetrtafvvalaxtkqhxeldvsogtt"),
        base_url="https://api.siliconflow.cn/v1"  # SiliconFlow API基础URL
    )
    
    # 视觉模型提示词（中文，用于户型布局分析）
    vision_prompt = """
    分析提供的户型图，详细描述布局，包括：
    - 卧室、卫生间、客厅、厨房及其他功能空间（如阳台、书房）的数量。
    - 每个功能空间的分布位置（例如，主卧位于东南角）。
    - 朝向（例如，客厅朝南，厨房朝北）。
    - 动线路径（例如，入口通向走廊连接客厅和卧室；动线是否高效）。
    - 整体结构：是高层住宅还是叠拼别墅？如可辨识，估算大致面积。
    - 任何显著特点，如开放式设计、自然采光潜力，或潜在问题如不规则形状。
    请以结构化的中文文本描述。
    """
    
    # LLM提示词（中文，用于户型特点分析）
    llm_prompt_template = """
    请根据以下户型图描述，给出总体评价，注意只需要总体评价，其他内容不要包括。
    请严格按照以下格式输出：
    ### 总体评价
    （2-3句话，简要总结，直观评价即可）
    
    """
    
    # 将图片编码为base64
    def encode_image(image_path):
        try:
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"无法编码图片 {image_path}: {str(e)}")
            return None
    
    # 分析单张户型图
    def analyze_floor_plan(image_path):
        # 编码图片
        base64_image = encode_image(image_path)
        if base64_image is None:
            return {
                "image_path": image_path,
                "layout_description": "",
                "analysis_text": f"错误：无法读取图片 {image_path}",
                "error": True
            }
        
        # 步骤1：使用视觉模型（SiliconFlow支持的视觉模型，例如qwen-vl）获取布局描述
        try:
            vision_response = client.chat.completions.create(
                model="Qwen/Qwen2.5-VL-32B-Instruct",  # SiliconFlow支持的视觉模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": vision_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"  # 假设为JPEG格式，需根据实际调整
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            layout_description = vision_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"视觉模型处理 {image_path} 失败: {str(e)}")
            return {
                "image_path": image_path,
                "layout_description": "",
                "analysis_text": f"错误：视觉模型处理失败 - {str(e)}",
                "error": True
            }
        
        # 步骤2：使用LLM（SiliconFlow支持的模型，例如DeepSeek-R1）生成分析文本
        try:
            llm_response = client.chat.completions.create(
                model="deepseek-ai/DeepSeek-R1",  # SiliconFlow支持的LLM模型
                messages=[
                    {
                        "role": "user",
                        "content": llm_prompt_template.format(description=layout_description)
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            analysis_text = llm_response.choices[0].message.content.strip()
        except Exception as e:
            print(f"LLM处理 {image_path} 失败: {str(e)}")
            return {
                "image_path": image_path,
                "layout_description": layout_description,
                "analysis_text": f"错误：LLM处理失败 - {str(e)}",
                "error": True
            }
        
        return {
            "image_path": image_path,
            "layout_description": layout_description,
            "analysis_text": analysis_text,
            "error": False
        }
    
    # 主流程：处理所有图片并保存结果到TXT
    timestamp = datetime.now().strftime("%Y%m%d")
    output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"{project_name}_户型分析.txt"
    
    results = []
    with open(output_file, "w", encoding="utf-8") as f:
        for path in image_paths:
            try:
                if not Path(path).exists():
                    error_msg = f"图片不存在: {path}\n"
                    f.write(error_msg)
                    print(error_msg)
                    results.append({
                        "image_path": path,
                        "layout_description": "",
                        "analysis_text": f"错误：图片不存在 - {path}",
                        "error": True
                    })
                    continue
                
                result = analyze_floor_plan(path)
                results.append(result)
                # 写入TXT文件
                f.write(f"户型图路径: {path}\n")
                f.write(f"分析结果:\n{result['analysis_text']}\n")
                f.write("="*50 + "\n\n")
                print(f"{path}的分析结果已保存到 {output_file}\n")
            except Exception as e:
                error_msg = f"处理{path}时出错：{str(e)}\n"
                f.write(error_msg)
                print(error_msg)
                results.append({
                    "image_path": path,
                    "layout_description": "",
                    "analysis_text": f"错误：处理失败 - {str(e)}",
                    "error": True
                })
    
    return {
        "output_file": str(output_file),
        "results": results
    }

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n户型分析结果:", result)