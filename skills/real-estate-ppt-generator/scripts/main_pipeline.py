#!/usr/bin/env python3
"""
Main Pipeline for Housing, Land, Supply, Deal, Visualization, Floor Plan Analysis,
Table Data Extraction, Slide Master Creation, Table Additions, Image and Text Insertions,
Surrounding Information Analysis, Customer Analysis, Customer Analysis Text Insertion,
and Surrounding Summary Insertion

请确保 utils/ 目录下存在对应模块并导出 run(...) 接口（或至少可用单参/双参回退）。
"""

from typing import Dict, Any
import os
import sys
from datetime import datetime

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

def main_pipeline(project_name: str = None, timestamp: str = None) -> Dict[str, Dict[str, Any]]:
    """Main pipeline function to execute data processing modules."""
    if project_name is None:
        project_name = input("请输入项目名称: ")
    
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d")
    
    # 动态导入utils模块
    try:
        from real_estate_ppt_utils.data_processor_cric_housing_parser import run as data_processor_cric_housing_parser
        from real_estate_ppt_utils.data_processor_cric_land_parser import run as data_processor_cric_land_parser
        from real_estate_ppt_utils.data_processor_analyze_real_estate_supply import run as data_processor_analyze_real_estate_supply
        from real_estate_ppt_utils.data_processor_extract_all_deal_table_style import run as data_processor_extract_all_deal_table_style
        from real_estate_ppt_utils.data_processor_draw_table_picture import run as data_processor_draw_table_picture
        from real_estate_ppt_utils.data_processor_picture_to_llm import run as data_processor_picture_to_llm
        from real_estate_ppt_utils.data_processor_extract_table_data import run as data_processor_extract_table_data
        from real_estate_ppt_utils.pptx_gen_create_gemdale_slide_master import run as pptx_gen_create_gemdale_slide_master
        from real_estate_ppt_utils.pptx_gen_add_data_table_to_slide import run as pptx_gen_add_data_table_to_slide
        from real_estate_ppt_utils.pptx_gen_add_analysis_table_to_slide import run as pptx_gen_add_analysis_table_to_slide
        from real_estate_ppt_utils.pptx_gen_add_picture_to_page2_lyf import run as pptx_gen_add_picture_to_page2_lyf
        from real_estate_ppt_utils.pptx_gen_add_picture_page3_lyf import run as pptx_gen_add_picture_page3_lyf
        from real_estate_ppt_utils.pptx_gen_add_txt_page3_lyf import run as pptx_gen_add_txt_page3_lyf
        from real_estate_ppt_utils.pptx_gen_add_table_to_page4_lyf import run as pptx_gen_add_table_to_page4_lyf
        from real_estate_ppt_utils.data_process_analyze_housing_around_llm import run as data_process_analyze_housing_around_llm
        from real_estate_ppt_utils.data_processor_analyze_customer import run as data_processor_analyze_customer
        from real_estate_ppt_utils.pptx_gen_add_txt_page5_lyf import run as pptx_gen_add_txt_page5_lyf
        from real_estate_ppt_utils.pptx_gen_add_surrounding_summary_to_page4 import run as pptx_gen_add_surrounding_summary_to_page4
        from real_estate_ppt_utils.data_processor_analyze_kaipan import run as data_processor_analyze_kaipan
        from real_estate_ppt_utils.pptx_gen_add_kaipan_table_to_page2 import run as pptx_gen_add_kaipan_table_to_page2
        from real_estate_ppt_utils.ppt_gen_add_kaipan_llm_to_page2 import run as ppt_gen_add_kaipan_llm_to_page2
        from real_estate_ppt_utils.data_process_kehu_pie_picture import run as data_process_kehu_pie_picture
        from real_estate_ppt_utils.pptx_gen_add_pie_picture_to_page5 import run as pptx_gen_add_pie_picture_to_page5
    except ImportError as e:
        print(f"导入模块失败: {e}")
        return {"error": f"模块导入失败: {str(e)}"}
    
    print(f"\n开始处理项目: {project_name}")
    print(f"时间戳: {timestamp}")
    
    # 创建工作目录
    working_dir = f"resources/working_data/{project_name}_{timestamp}"
    os.makedirs(working_dir, exist_ok=True)
    
    results = {}
    
    # 1. 住房数据解析
    print("\n执行住房数据解析...")
    housing_result = data_processor_cric_housing_parser(project_name, f"{working_dir}/{project_name}_基本信息.txt")
    results["housing_data"] = housing_result
    
    # 2. 土地数据解析
    print("\n执行土地数据解析...")
    land_result = data_processor_cric_land_parser(project_name, f"{working_dir}/{project_name}_土地信息.txt")
    results["land_data"] = land_result
    
    # 3. 供应数据分析
    print("\n执行供应数据分析...")
    supply_result = data_processor_analyze_real_estate_supply(project_name, f"{working_dir}/{project_name}_供应明细底表.xlsx")
    results["supply_data"] = supply_result
    
    # 4. 成交数据分析
    print("\n执行成交数据分析...")
    deal_result = data_processor_extract_all_deal_table_style(project_name, f"{working_dir}/{project_name}_成交分析结果.xlsx")
    results["deal_data"] = deal_result
    
    # 5. 开盘（Kaipan）数据分析
    print("\n执行开盘（Kaipan）数据分析...")
    kaipan_analysis_result = None
    try:
        kaipan_analysis_result = data_processor_analyze_kaipan(
            project_name, f"{working_dir}/{project_name}_开盘信息.xlsx"
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
    results["kaipan_analysis_data"] = kaipan_analysis_result
    
    # 6. 成交数据可视化
    print("\n执行成交数据可视化...")
    visualization_result = data_processor_draw_table_picture(project_name)
    results["visualization_data"] = visualization_result
    
    # 7. 户型图分析
    print("\n执行户型图分析...")
    floor_plan_result = data_processor_picture_to_llm(project_name)
    results["floor_plan_data"] = floor_plan_result
    
    # 8. 表格数据提取
    print("\n执行表格数据提取...")
    table_data_result = data_processor_extract_table_data(project_name)
    results["table_data"] = table_data_result
    
    # 9. 客户地域来源饼图生成
    print("\n执行客户地域来源饼图生成...")
    data_process_kehu_pie_picture_result = None
    try:
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
    results["kehu_pie_picture_data"] = data_process_kehu_pie_picture_result
    
    # 10. 幻灯片模板生成
    print("\n执行幻灯片模板生成...")
    slide_master_result = pptx_gen_create_gemdale_slide_master(project_name)
    results["slide_master_data"] = slide_master_result
    
    # 11. 项目数据表格添加到幻灯片
    print("\n执行项目数据表格添加到幻灯片...")
    table_add_result = pptx_gen_add_data_table_to_slide(project_name, left_position=7.5)
    results["table_add_data"] = table_add_result
    
    # 12. 分析表格添加到幻灯片
    print("\n执行分析表格添加到幻灯片...")
    analysis_table_result = pptx_gen_add_analysis_table_to_slide(project_name, left_position=1.0, top_position=4.0)
    results["analysis_table_data"] = analysis_table_result
    
    # 13. 开盘LLM文字添加到幻灯片（第2页）
    print("\n执行开盘LLM文字添加到幻灯片（第2页）...")
    ppt_gen_add_kaipan_llm_to_page2_result = None
    try:
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
    results["ppt_gen_add_kaipan_llm_to_page2_data"] = ppt_gen_add_kaipan_llm_to_page2_result
    
    # 14. 图片和标题添加到幻灯片（第2页）
    print("\n执行图片和标题添加到幻灯片（第2页）...")
    image_page2_result = pptx_gen_add_picture_to_page2_lyf(project_name)
    results["image_page2_data"] = image_page2_result
    
    # 15. 开盘表格添加到幻灯片（第2页）
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
    results["kaipan_table_page2_data"] = kaipan_table_page2_result
    
    # 16. 户型分析文本和图片添加到幻灯片（第3页）
    print("\n执行户型分析文本和图片添加到幻灯片（第3页）...")
    picture_page3_result = pptx_gen_add_picture_page3_lyf(project_name)
    text_page3_result = pptx_gen_add_txt_page3_lyf(project_name)
    results["picture_page3_data"] = picture_page3_result
    results["text_page3_data"] = text_page3_result
    
    # 17. 客户分析
    print("\n执行客户分析...")
    customer_analysis_result = data_processor_analyze_customer(project_name)
    results["customer_analysis_data"] = customer_analysis_result
    
    # 18. 周边信息总结生成
    print("\n执行周边信息总结生成...")
    surrounding_summary_result = data_process_analyze_housing_around_llm(project_name)
    results["surrounding_summary_data"] = surrounding_summary_result
    
    # 19. 装修表格添加到幻灯片（第4页）
    print("\n执行装修表格添加到幻灯片（第4页）...")
    page4_table_result = pptx_gen_add_table_to_page4_lyf(project_name)
    results["page4_table_data"] = page4_table_result
    
    # 20. 周边信息总结插入到幻灯片（第4页）
    print("\n执行周边信息总结插入到幻灯片（第4页）...")
    surrounding_summary_page4_result = pptx_gen_add_surrounding_summary_to_page4(project_name)
    results["surrounding_summary_page4_data"] = surrounding_summary_page4_result
    
    # 21. 客户分析文本添加到幻灯片（第5页）
    print("\n执行客户分析文本添加到幻灯片（第5页）...")
    customer_analysis_page5_result = pptx_gen_add_txt_page5_lyf(project_name, timestamp)
    results["customer_analysis_page5_data"] = customer_analysis_page5_result
    
    # 22. 将地域来源饼图插入到幻灯片（第5页）
    print("\n执行将地域来源饼图插入到幻灯片（第5页）...")
    pptx_gen_add_pie_picture_to_page5_result = None
    try:
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
    results["pptx_gen_add_pie_picture_to_page5_data"] = pptx_gen_add_pie_picture_to_page5_result
    
    print("\nPipeline 执行完成！")
    return results

if __name__ == "__main__":
    final_result = main_pipeline()
    print("\nPipeline 执行完成，最终结果:")
    for key, value in final_result.items():
        print(f"{key}: {value}")