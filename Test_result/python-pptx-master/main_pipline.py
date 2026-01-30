#!/usr/bin/env python3
"""
Main Pipeline for Housing, Land, Supply, Deal, Visualization, Floor Plan Analysis,
Table Data Extraction, Slide Master Creation, Table Additions, Image and Text Insertions,
Surrounding Information Analysis, Customer Analysis, Customer Analysis Text Insertion,
and Surrounding Summary Insertion



请确保 utils/ 目录下存在对应模块并导出 run(...) 接口（或至少可用单参/双参回退）。
"""

from typing import Dict, Any
from utils.data_processor_cric_housing_parser import run as data_processor_cric_housing_parser
from utils.data_processor_cric_land_parser import run as data_processor_cric_land_parser
from utils.data_processor_analyze_real_estate_supply import run as data_processor_analyze_real_estate_supply
from utils.data_processor_extract_all_deal_table_style import run as data_processor_extract_all_deal_table_style
from utils.data_processor_draw_table_picture import run as data_processor_draw_table_picture
from utils.data_processor_picture_to_llm import run as data_processor_picture_to_llm
from utils.data_processor_extract_table_data import run as data_processor_extract_table_data
from utils.pptx_gen_create_gemdale_slide_master import run as pptx_gen_create_gemdale_slide_master
from utils.pptx_gen_add_data_table_to_slide import run as pptx_gen_add_data_table_to_slide
from utils.pptx_gen_add_analysis_table_to_slide import run as pptx_gen_add_analysis_table_to_slide
from utils.pptx_gen_add_picture_to_page2_lyf import run as pptx_gen_add_picture_to_page2_lyf
from utils.pptx_gen_add_picture_page3_lyf import run as pptx_gen_add_picture_page3_lyf
from utils.pptx_gen_add_txt_page3_lyf import run as pptx_gen_add_txt_page3_lyf
from utils.pptx_gen_add_table_to_page4_lyf import run as pptx_gen_add_table_to_page4_lyf
from utils.data_process_analyze_housing_around_llm import run as data_process_analyze_housing_around_llm
from utils.data_processor_analyze_customer import run as data_processor_analyze_customer
from utils.pptx_gen_add_txt_page5_lyf import run as pptx_gen_add_txt_page5_lyf
from utils.pptx_gen_add_surrounding_summary_to_page4 import run as pptx_gen_add_surrounding_summary_to_page4
from utils.data_processor_analyze_kaipan import run as data_processor_analyze_kaipan
from utils.pptx_gen_add_kaipan_table_to_page2 import run as pptx_gen_add_kaipan_table_to_page2
from utils.ppt_gen_add_kaipan_llm_to_page2 import run as ppt_gen_add_kaipan_llm_to_page2
from utils.data_process_kehu_pie_picture import run as data_process_kehu_pie_picture
from utils.pptx_gen_add_pie_picture_to_page5 import run as pptx_gen_add_pie_picture_to_page5
# -----------------------------------------------------------------

from datetime import datetime

def main_pipeline() -> Dict[str, Dict[str, Any]]:
    """Main pipeline function to execute data processing modules."""
    project_name = input("请输入项目名称: ")
    timestamp = datetime.now().strftime("%Y%m%d")
    
    print("\n执行住房数据解析...")
    housing_result = data_processor_cric_housing_parser(project_name, f"resources/working_data/{project_name}_{timestamp}/{project_name}_基本信息.txt")
    
    print("\n执行土地数据解析...")
    land_result = data_processor_cric_land_parser(project_name, f"resources/working_data/{project_name}_{timestamp}/{project_name}_土地信息.txt")
    
    print("\n执行供应数据分析...")
    supply_result = data_processor_analyze_real_estate_supply(project_name, f"resources/working_data/{project_name}_{timestamp}/{project_name}_供应明细底表.xlsx")
    
    print("\n执行成交数据分析...")
    deal_result = data_processor_extract_all_deal_table_style(project_name, f"resources/working_data/{project_name}_{timestamp}/{project_name}_成交分析结果.xlsx")
    
    # 新增：开盘（Kaipan）数据分析（放在成交数据分析之后）
    print("\n执行开盘（Kaipan）数据分析...")
    kaipan_analysis_result = None
    try:
        kaipan_analysis_result = data_processor_analyze_kaipan(
            project_name, f"resources/working_data/{project_name}_{timestamp}/{project_name}_开盘信息.xlsx"
        )
    except TypeError:
        try:
            kaipan_analysis_result = data_processor_analyze_kaipan(project_name)
        except Exception as e:
            print(f"[WARN] data_processor_analyze_kaipan 调用失败: {e}")
            kaipan_analysis_result = {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[WARN] data_processor_analyze_kaipan 调用异常: {e}")
        kaipan_analysis_result = {"success": False, "error": str(e)}
    
    print("\n执行成交数据可视化...")
    visualization_result = data_processor_draw_table_picture(project_name)
    
    print("\n执行户型图分析...")
    floor_plan_result = data_processor_picture_to_llm(project_name)
    
    
    print("\n执行表格数据提取...")
    table_data_result = data_processor_extract_table_data(project_name)
    
    print("\n执行幻灯片模板生成...")
    slide_master_result = pptx_gen_create_gemdale_slide_master(project_name)
    
    print("\n执行项目数据表格添加到幻灯片...")
    table_add_result = pptx_gen_add_data_table_to_slide(project_name,left_position=7.5)
    
    print("\n执行分析表格添加到幻灯片...")
    analysis_table_result = pptx_gen_add_analysis_table_to_slide(project_name,left_position=1.0,top_position=4.0)
    
    # 新增：在分析表格添加后，插入开盘LLM文字到第2页（或相应位置）
    print("\n执行开盘LLM文字添加到幻灯片（第2页）...")
    ppt_gen_add_kaipan_llm_to_page2_result = None
    try:
        # 常见签名：project_name, timestamp
        ppt_gen_add_kaipan_llm_to_page2_result = ppt_gen_add_kaipan_llm_to_page2(project_name, timestamp)
    except TypeError:
        try:
            ppt_gen_add_kaipan_llm_to_page2_result = ppt_gen_add_kaipan_llm_to_page2(project_name)
        except Exception as e:
            print(f"[WARN] ppt_gen_add_kaipan_llm_to_page2 调用失败: {e}")
            ppt_gen_add_kaipan_llm_to_page2_result = {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[WARN] ppt_gen_add_kaipan_llm_to_page2 调用异常: {e}")
        ppt_gen_add_kaipan_llm_to_page2_result = {"success": False, "error": str(e)}
    
    print("\n执行图片和标题添加到幻灯片（第2页）...")
    image_page2_result = pptx_gen_add_picture_to_page2_lyf(project_name)
    
    # 新增：将开盘（Kaipan）表格插入到第2页（位于图片/标题之后）
    print("\n执行开盘表格添加到幻灯片（第2页）...")
    kaipan_table_page2_result = None
    try:
        kaipan_table_page2_result = pptx_gen_add_kaipan_table_to_page2(project_name)
    except TypeError:
        try:
            kaipan_table_page2_result = pptx_gen_add_kaipan_table_to_page2(project_name, timestamp)
        except Exception as e:
            print(f"[WARN] pptx_gen_add_kaipan_table_to_page2 调用失败: {e}")
            kaipan_table_page2_result = {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[WARN] pptx_gen_add_kaipan_table_to_page2 调用异常: {e}")
        kaipan_table_page2_result = {"success": False, "error": str(e)}
    
    print("\n执行户型分析文本和图片添加到幻灯片（第3页）...")
    picture_page3_result = pptx_gen_add_picture_page3_lyf(project_name)
    text_page3_result = pptx_gen_add_txt_page3_lyf(project_name)
    
    print("\n执行客户分析...")
    customer_analysis_result = data_processor_analyze_customer(project_name)

     # 新增：从客户分析文本生成地域来源饼图
    print("\n执行客户地域来源饼图生成（调试/图片）...")
    data_process_kehu_pie_picture_result = None
    try:
        # 优先传入 project_name + timestamp
        data_process_kehu_pie_picture_result = data_process_kehu_pie_picture(project_name, timestamp)
    except TypeError:
        try:
            data_process_kehu_pie_picture_result = data_process_kehu_pie_picture(project_name)
        except Exception as e:
            print(f"[WARN] data_process_kehu_pie_picture 调用失败: {e}")
            data_process_kehu_pie_picture_result = {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[WARN] data_process_kehu_pie_picture 调用异常: {e}")
        data_process_kehu_pie_picture_result = {"success": False, "error": str(e)}
    
    print("\n执行周边信息总结生成...")
    surrounding_summary_result = data_process_analyze_housing_around_llm(project_name)
    
    print("\n执行装修表格添加到幻灯片（第4页）...")
    page4_table_result = pptx_gen_add_table_to_page4_lyf(project_name)
    
    print("\n执行周边信息总结插入到幻灯片（第4页）...")
    surrounding_summary_page4_result = pptx_gen_add_surrounding_summary_to_page4(project_name)
    
    print("\n执行客户分析文本添加到幻灯片（第5页）...")
    customer_analysis_page5_result = pptx_gen_add_txt_page5_lyf(project_name, timestamp)
    
    # 新增：把地域来源饼图插入到第5页右侧（最后步骤）
    print("\n执行将地域来源饼图插入到幻灯片（第5页）...")
    pptx_gen_add_pie_picture_to_page5_result = None
    try:
        # 常见签名：project_name, timestamp
        pptx_gen_add_pie_picture_to_page5_result = pptx_gen_add_pie_picture_to_page5(project_name, timestamp)
    except TypeError:
        try:
            pptx_gen_add_pie_picture_to_page5_result = pptx_gen_add_pie_picture_to_page5(project_name)
        except Exception as e:
            print(f"[WARN] pptx_gen_add_pie_picture_to_page5 调用失败: {e}")
            pptx_gen_add_pie_picture_to_page5_result = {"success": False, "error": str(e)}
    except Exception as e:
        print(f"[WARN] pptx_gen_add_pie_picture_to_page5 调用异常: {e}")
        pptx_gen_add_pie_picture_to_page5_result = {"success": False, "error": str(e)}
    
    print("\n执行完毕：汇总结果...")
    combined_result = {
        "housing_data": housing_result,
        "land_data": land_result,
        "supply_data": supply_result,
        "deal_data": deal_result,
        "kaipan_analysis_data": kaipan_analysis_result,
        "visualization_data": visualization_result,
        "floor_plan_data": floor_plan_result,
        "kehu_pie_picture_data": data_process_kehu_pie_picture_result,  # 新增
        "table_data": table_data_result,
        "slide_master_data": slide_master_result,
        "table_add_data": table_add_result,
        "analysis_table_data": analysis_table_result,
        "ppt_gen_add_kaipan_llm_to_page2_data": ppt_gen_add_kaipan_llm_to_page2_result,  # 新增
        "image_page2_data": image_page2_result,
        "kaipan_table_page2_data": kaipan_table_page2_result,
        "picture_page3_data": picture_page3_result,
        "text_page3_data": text_page3_result,
        "customer_analysis_data": customer_analysis_result,
        "surrounding_summary_data": surrounding_summary_result,
        "page4_table_data": page4_table_result,
        "surrounding_summary_page4_data": surrounding_summary_page4_result,
        "customer_analysis_page5_data": customer_analysis_page5_result,
        "pptx_gen_add_pie_picture_to_page5_data": pptx_gen_add_pie_picture_to_page5_result  # 新增
    }
    
    return combined_result

if __name__ == "__main__":
    final_result = main_pipeline()
    print("\nPipeline 执行完成，最终结果:")
    print(f"住房数据: {final_result['housing_data']}")
    print(f"土地数据: {final_result['land_data']}")
    print(f"供应数据: {final_result['supply_data']}")
    print(f"成交数据: {final_result['deal_data']}")
    print(f"开盘分析数据: {final_result['kaipan_analysis_data']}")
    print(f"可视化数据: {final_result['visualization_data']}")
    print(f"户型图分析数据: {final_result['floor_plan_data']}")
    print(f"地域来源饼图数据: {final_result['kehu_pie_picture_data']}")
    print(f"表格数据: {final_result['table_data']}")
    print(f"幻灯片模板数据: {final_result['slide_master_data']}")
    print(f"项目表格添加数据: {final_result['table_add_data']}")
    print(f"分析表格数据: {final_result['analysis_table_data']}")
    print(f"第2页开盘LLM文字添加数据: {final_result['ppt_gen_add_kaipan_llm_to_page2_data']}")
    print(f"第2页图片添加数据: {final_result['image_page2_data']}")
    print(f"第2页开盘表格添加数据: {final_result['kaipan_table_page2_data']}")
    print(f"第3页户型分析图片添加数据: {final_result['picture_page3_data']}")
    print(f"第3页户型分析文本添加数据: {final_result['text_page3_data']}")
    print(f"客户分析数据: {final_result['customer_analysis_data']}")
    print(f"周边信息总结数据: {final_result['surrounding_summary_data']}")
    print(f"第4页装修表格数据: {final_result['page4_table_data']}")
    print(f"第4页周边信息总结插入数据: {final_result['surrounding_summary_page4_data']}")
    print(f"第5页客户分析文本添加数据: {final_result['customer_analysis_page5_data']}")
    print(f"第5页饼图插入数据: {final_result['pptx_gen_add_pie_picture_to_page5_data']}")
