#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Estate Deal Data Analysis Script
Analyzes deal data from Excel file to compute monthly sales counts and average prices by category
"""

import pandas as pd
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def run(project_name: str, file_path: str = "resources/working_data/all_deal_with_date_data.xlsx") -> Dict[str, Any]:
    """Run the deal data analysis with a given project name and file path."""
    
    # 固定文件路径
    file_path = Path(file_path)
    
    # 检查文件是否存在
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return {}
    
    try:
        # 读取 Excel 文件，无表头
        df = pd.read_excel(file_path, header=None)
        
        # 模糊匹配：检查第二列是否包含项目名称的部分内容
        second_column_data = df.iloc[:, 1].astype(str).str.strip()
        is_presale_license = not any(second_column_data.str.contains(project_name, case=False, na=False))
        
        # 定义表头
        if is_presale_license:
            # 如果是预售证，删除第二列并使用新的表头
            df = df.drop(columns=1)  # 删除第二列（预售证）
            header = ['成交日期', '项目', '楼栋', '房间', '物业类型', '户型', '面积', '单价', '成交总价']
        else:
            # 如果是项目，保留原表头
            header = ['成交日期', '项目', '楼栋', '房间', '物业类型', '户型', '面积', '单价', '成交总价']
        
        # 将表头赋值给 DataFrame
        df.columns = header
    except Exception as e:
        print(f"读取文件失败：{e}")
        return {}
    
    # 确保必要的字段存在
    required_columns = ['成交日期', '物业类型', '户型', '面积', '成交总价']
    if not all(col in df.columns for col in required_columns):
        print("xlsx文件缺少必要的字段：成交日期、物业类型、户型、面积、成交总价")
        return {}
    
    # 清理成交日期格式，提取有效的日期字符串
    def extract_date_string(date_str):
        # Handle None or NaN
        if pd.isna(date_str):
            return None
        
        # Convert to string
        date_str = str(date_str)
        
        # Try to extract date pattern (e.g., 2025/08/27)
        date_match = re.search(r'\b(\d{4}/\d{2}/\d{2})\b', date_str)
        if date_match:
            return date_match.group(1)
        
        # Fallback: remove brackets, quotes, newlines, and clean up
        cleaned = re.sub(r'[\[\]"\n\r_\x000D\s]', '', date_str)
        return cleaned if cleaned else None
    
    df['成交日期'] = df['成交日期'].apply(extract_date_string)
    
    # 将成交日期转换为 datetime 格式
    try:
        df['成交日期'] = pd.to_datetime(df['成交日期'], format='%Y/%m/%d', errors='coerce')
    except Exception as e:
        print(f"日期格式转换失败：{e}")
        return {}
    
    print(df['成交日期'].head())
    # 过滤无效日期
    invalid_dates = df['成交日期'].isna().sum()
    if invalid_dates > 0:
        print(f"警告：{invalid_dates} 条日期记录无效，已被移除")
    df = df.dropna(subset=['成交日期'])
    
    # 清理面积和成交总价中的逗号并转换为数值
    df['面积'] = df['面积'].astype(str).str.replace(',', '', regex=False).str.strip()
    df['成交总价'] = df['成交总价'].astype(str).str.replace(',', '', regex=False).str.strip()
    
    # 将面积和成交总价转换为数值类型
    try:
        df['面积'] = pd.to_numeric(df['面积'], errors='coerce')
        df['成交总价'] = pd.to_numeric(df['成交总价'], errors='coerce')
    except Exception as e:
        print(f"面积或成交总价转换为数值失败：{e}")
        return {}
    
    # 检查无效数值
    invalid_area = df['面积'].isna().sum()
    invalid_price = df['成交总价'].isna().sum()
    if invalid_area > 0 or invalid_price > 0:
        print(f"警告：面积列有 {invalid_area} 条无效值，成交总价列有 {invalid_price} 条无效值，已被移除")
        df = df.dropna(subset=['面积', '成交总价'])
    
    # 检查面积列是否有零或负值
    if any(df['面积'] <= 0):
        print("面积列包含零或负值，请检查数据！")
        return {}
    
    # 用户输入分类方式
    classification = input("请输入分类方式（户型 或 物业类型）：").strip()
    
    # 按月分组，并添加月份列
    df['时间'] = df['成交日期'].dt.to_period('M').astype(str)
    
    # 动态获取分类值并过滤总套数少于20的分类
    if classification == '户型':
        df['分类'] = df['户型'].fillna('其他')
        # 计算每个户型的总套数
        category_counts = df['分类'].value_counts()
        # 筛选出总套数 >= 20 的分类
        valid_categories = category_counts[category_counts >= 20].index.tolist()
        # 过滤数据，只保留有效分类
        df = df[df['分类'].isin(valid_categories)]
        categories = valid_categories
    elif classification == '物业类型':
        df['分类'] = df['物业类型'].fillna('其他')
        # 计算每个物业类型的总套数
        category_counts = df['分类'].value_counts()
        # 筛选出总套数 >= 20 的分类
        valid_categories = category_counts[category_counts >= 20].index.tolist()
        # 过滤数据，只保留有效分类
        df = df[df['分类'].isin(valid_categories)]
        categories = valid_categories
    else:
        print("无效输入，请输入'户型'或'物业类型'。")
        return {}
    
    # 按月和分类统计销售套数
    sales_count = df.groupby(['时间', '分类']).size().unstack(fill_value=0)
    
    # 按月和分类计算成交均价 = sum(成交总价) / sum(面积)
    monthly_avg_price = df.groupby(['时间', '分类']).apply(
        lambda x: x['成交总价'].sum() / x['面积'].sum() if x['面积'].sum() > 0 else 0,
        include_groups=False
    ).round(2).unstack(fill_value=0)
    
    # 重命名均价列，添加后缀以区分
    monthly_avg_price.columns = [f'{col}_成交均价 (元/m²)' for col in monthly_avg_price.columns]
    
    # 合并结果并重置索引
    result = sales_count.join(monthly_avg_price).reset_index()
    
    # 动态生成列顺序：时间 + 每个分类的销售套数和均价
    columns_order = ['时间']
    for category in categories:
        if category in result.columns:
            columns_order.append(category)
        if f'{category}_成交均价 (元/m²)' in result.columns:
            columns_order.append(f'{category}_成交均价 (元/m²)')
    
    # 确保所有分类的列都存在，若不存在则填充0
    for category in categories:
        if category not in result.columns:
            result[category] = 0
        if f'{category}_成交均价 (元/m²)' not in result.columns:
            result[f'{category}_成交均价 (元/m²)'] = 0
    
    # 按动态列顺序重新排序结果
    result = result[columns_order]
    
    # 输出结果表格
    if not result.empty:
        print(result)
        # 保存结果到 Excel
        try:
            timestamp = datetime.now().strftime("%Y%m%d")
            output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{project_name}_成交分析结果.xlsx"
            
            # 写入 Excel（保持原格式）
            result.to_excel(output_path, index=False, engine="openpyxl")
            
            print(f"结果已保存到 {output_path}")
        except Exception as e:
            print(f"保存结果到 Excel 失败：{e}")
    else:
        print("结果表格为空，请检查数据！")
    
    # 返回分析结果
    return {
        'sales_data': result.to_dict(),
        'classification': classification,
        'categories': categories
    }

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n分析结果:", result)