# -*- coding: utf-8 -*-
"""
Table Data Extractor
Extracts specified data from housing and land JSON files to create table data structure
"""

import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List

def extract_table_data_from_json(housing_data_path: str, land_data_path: str) -> List[List[str]]:
    """
    Extract specified data from housing and land JSON files to create table data structure.
    
    Parameters:
    - housing_data_path: str, path to housing data JSON file
    - land_data_path: str, path to land data JSON file
    
    Returns:
    - list: 2D array (16x2) table data compatible with add_table_to_slide function
    """
    
    # Initialize the keys we need to extract
    target_keys = [
        "开发商",
        "物业管理", 
        "拿地时间",
        "最早开盘时间",
        "最晚交房时间",
        "楼板价",
        "建筑面积",
        "容积率",
        "物业类型",
        "主力户型",
        "总户数",
        "车位配比",
        "成交均价",
        "精装成本",
        "客户特点",
        "项目卖点"
    ]
    
    table_data = []
    
    # Load housing data
    try:
        with open(housing_data_path, 'r', encoding='utf-8') as f:
            housing_data = json.load(f)
    except Exception as e:
        print(f"无法加载住房数据文件 {housing_data_path}: {str(e)}")
        housing_data = {}
    
    # Load land data
    try:
        with open(land_data_path, 'r', encoding='utf-8') as f:
            land_data = json.load(f)
    except Exception as e:
        print(f"无法加载土地数据文件 {land_data_path}: {str(e)}")
        land_data = {}
    
    # Extract data for each target key
    for key in target_keys:
        value = ""
        
        if key == "开发商":
            # Found in both files - housing data has priority
            if "企业信息" in housing_data and "开发商" in housing_data["企业信息"]:
                value = housing_data["企业信息"]["开发商"]
            elif "土地概要信息" in land_data and "开发商" in land_data["土地概要信息"]:
                value = land_data["土地概要信息"]["开发商"]
        
        elif key == "物业管理":
            # Found in housing data
            if "企业信息" in housing_data and "物业管理" in housing_data["企业信息"]:
                value = housing_data["企业信息"]["物业管理"]
        
        elif key == "拿地时间":
            # Found in land data as 成交时间
            if "成交信息" in land_data and "成交时间" in land_data["成交信息"]:
                value = land_data["成交信息"]["成交时间"]
        
        elif key == "最早开盘时间":
            # Found in housing data
            if "基本信息" in housing_data and "最早开盘时间" in housing_data["基本信息"]:
                value = housing_data["基本信息"]["最早开盘时间"]
        
        elif key == "最晚交房时间":
            # Found in housing data
            if "基本信息" in housing_data and "最晚交房时间" in housing_data["基本信息"]:
                value = housing_data["基本信息"]["最晚交房时间"]
        
        elif key == "楼板价":
            # Found in land data
            if "成交信息" in land_data and "楼板价" in land_data["成交信息"]:
                value = land_data["成交信息"]["楼板价"]
        
        elif key == "建筑面积":
            # Found in both files - housing data has priority
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"] and "总建面积" in housing_data["产品综览"]["overview"]:
                value = housing_data["产品综览"]["overview"]["总建面积"]
            elif "基本信息" in land_data and "总建面积" in land_data["基本信息"]:
                value = land_data["基本信息"]["总建面积"]
        
        elif key == "容积率":
            # Found in both files - housing data has priority
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"] and "容积率" in housing_data["产品综览"]["overview"]:
                value = housing_data["产品综览"]["overview"]["容积率"]
            elif "基本信息" in land_data and "容积率" in land_data["基本信息"]:
                value = land_data["基本信息"]["容积率"]
        
        elif key == "物业类型":
            # Found in housing data
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"] and "物业类型" in housing_data["产品综览"]["overview"]:
                value = housing_data["产品综览"]["overview"]["物业类型"]
        
        elif key == "主力户型":
            # Extract from housing data product overview description
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"]:
                overview_text = str(housing_data["产品综览"]["overview"])
                # Look for patterns like "三房 面积: 97.72-142.41 ㎡" or similar
                room_patterns = re.findall(r'(\d+房)\s*面积:\s*([\d\.\-]+)\s*㎡', overview_text)
                if room_patterns:
                    value = "; ".join([f"{room[0]}({room[1]}㎡)" for room in room_patterns])
        
        elif key == "总户数":
            # Found in housing data
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"] and "规划户数" in housing_data["产品综览"]["overview"]:
                value = housing_data["产品综览"]["overview"]["规划户数"]
        
        elif key == "车位配比":
            # Found in housing data
            if "产品综览" in housing_data and "overview" in housing_data["产品综览"] and "车位配比" in housing_data["产品综览"]["overview"]:
                value = housing_data["产品综览"]["overview"]["车位配比"]
        
        elif key == "成交均价":
            # Extract from housing data opening info
            if "开盘信息" in housing_data:
                for opening in housing_data["开盘信息"]:
                    if "开盘描述" in opening and isinstance(opening["开盘描述"], list):
                        for desc in opening["开盘描述"]:
                            if "均价" in str(desc):
                                # Look for patterns like "均价为64000元/㎡" or "销售均价62962元/㎡"
                                price_match = re.search(r'均价[为是]?(\d+(?:,\d+)*(?:\.\d+)?)\s*元/㎡', str(desc))
                                if price_match:
                                    value = f"{price_match.group(1)}元/㎡"
                                    break
                        if value:
                            break
        
        elif key == "精装成本":
            # Found in housing data decoration info
            if "装修情况" in housing_data and "general_info" in housing_data["装修情况"] and "装修价格" in housing_data["装修情况"]["general_info"]:
                value = housing_data["装修情况"]["general_info"]["装修价格"]
        
        elif key == "客户特点":
            # No direct mapping found in data
            value = "暂无数据"
        
        elif key == "项目卖点":
            # No direct mapping found in data
            value = "暂无数据"
        
        table_data.append([key, value if value else "暂无数据"])
    
    return table_data

def run(project_name: str, housing_data_path: str = None, land_data_path: str = None) -> Dict[str, Any]:
    """
    Run the table data extraction with a given project name and optional file paths.
    
    Parameters:
    - project_name: str, name of the project
    - housing_data_path: str, path to housing data JSON file (optional)
    - land_data_path: str, path to land data JSON file (optional)
    
    Returns:
    - dict: Contains the extracted table data
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Set default file paths if not provided
    if housing_data_path is None:
        housing_data_path = os.path.join("resources", "working_data", f"{project_name}_{timestamp}", "processed_data", f"{project_name}_房子基本信息.json")
    
    if land_data_path is None:
        land_data_path = os.path.join("resources", "working_data", f"{project_name}_{timestamp}", "processed_data", f"{project_name}_土地基本信息.json")
    
    # Check if files exist
    if not os.path.exists(housing_data_path):
        print(f"住房数据文件不存在: {housing_data_path}")
        return {"table_data": []}
    
    if not os.path.exists(land_data_path):
        print(f"土地数据文件不存在: {land_data_path}")
        return {"table_data": []}
    
    # Extract table data
    table_data = extract_table_data_from_json(housing_data_path, land_data_path)
    
    return {"table_data": table_data}

if __name__ == "__main__":
    # For testing purposes, use a default project name
    project_name = "华发四季半岛"
    result = run(project_name=project_name)
    
    print("Extracted 16x2 table data:")
    print("=" * 50)
    for row in result["table_data"]:
        print(f"{row[0]}: {row[1]}")
    
    print("\nFormatted for add_table_to_slide:")
    print("=" * 50)
    print("table_data = [")
    for row in result["table_data"]:
        print(f"    [\"{row[0]}\", \"{row[1]}\"],")
    print("]")