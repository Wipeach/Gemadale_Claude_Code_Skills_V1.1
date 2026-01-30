from typing import *
import os
import json
import datetime

from openai import OpenAI
from openai.types.chat.chat_completion import Choice

def run(project_name: str) -> None:
    # Initialize OpenAI client
    client = OpenAI(
        base_url="https://api.moonshot.cn/v1",
        api_key="sk-Ghgw4tuUZ9KJfGCgeymdRtVDkySjywunNiuc9M3oLjvpbBhT",
    )

    # Search tool implementation
    def search_impl(arguments: Dict[str, Any]) -> Any:
        return arguments

    def chat(messages) -> Choice:
        completion = client.chat.completions.create(
            model="kimi-k2-0905-preview",
            messages=messages,
            temperature=0.6,
            max_tokens=32768,
            tools=[
                {
                    "type": "builtin_function",
                    "function": {
                        "name": "$web_search",
                    },
                }
            ]
        )
        return completion.choices[0]

    # Create messages
    messages = [
    {"role": "system", "content": "你是 Kimi。"},
    {
        "role": "user",
        "content": """请检索“上海华发四季半岛”，地址：闵行颛桥鑫都路2288弄。  
请生成购房客群分析，要求：  
1. 输出结构化板块（如积分段、地域来源、支付力、家庭生命周期、职业特征、购房动机、典型客户画像等），每块内容控制在1-2句话。  
2. 在“地域来源”板块中，需明确来源（如闵行本地、长三角外溢、外省市等），并给出各来源的占比（必须给出%），合计100%。  
3. 结论部分需简要概括核心客群特征。  
4. 全文简明扼要，避免冗长描述，总长度不超过200字。  

输出示例（格式）：  
上海·华发四季半岛（闵行颛桥，鑫都路2288弄）  
主要购房客群画像（2022-2023年开盘期）

1. 积分段  
   入围积分≈55，低于周边竞品，属“低积分友好盘”。  

2. 地域来源  
   本地改善35%，5号线沿线40%，浦东/徐汇外溢20%，外省投资客5%。  

3. 支付力  
   总价段650-1000万，首付比例50-70%，月供1.3-1.8万。  

4. 家庭生命周期  
   新婚+首孩家庭为主，少量三代同堂改善。  

5. 职业特征  
   科技园区+工业区白领为核心，年收40-70万。  

6. 购房动机  
   通勤便利、价格洼地、学区预期。  

结论  
以5号线沿线科技产业白领和本地刚改家庭为主，投资客占比小，总体偏刚需-刚改。
"""
    }
]


    # Process chat completion
    finish_reason = None
    choice = None
    while finish_reason is None or finish_reason == "tool_calls":
        choice = chat(messages)
        finish_reason = choice.finish_reason
        if finish_reason == "tool_calls":
            messages.append(choice.message)
            for tool_call in choice.message.tool_calls:
                tool_call_name = tool_call.function.name
                tool_call_arguments = json.loads(tool_call.function.arguments)
                if tool_call_name == "$web_search":
                    tool_result = search_impl(tool_call_arguments)
                else:
                    tool_result = f"Error: unable to find tool by name '{tool_call_name}'"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call_name,
                    "content": json.dumps(tool_result),
                })

    # Create output directory
    timestamp = datetime.datetime.now().strftime("%Y%m%d")
    output_dir = f"resources/working_data/{project_name}_{timestamp}/processed_data"
    os.makedirs(output_dir, exist_ok=True)

    # Save to file
    output_path = f"{output_dir}/{project_name}_客户分析.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(choice.message.content + "\n")

if __name__ == '__main__':
    run("default_project")