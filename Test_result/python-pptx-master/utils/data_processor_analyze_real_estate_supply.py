#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Estate Supply Data Analysis Script
Analyzes supply data from Excel file to determine area ranges and room types by building type
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
from datetime import datetime
from typing import Dict, Any
warnings.filterwarnings('ignore')

# Configure pandas display options
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 50)

def categorize_area(area):
    """Categorize area into standard Chinese real estate ranges"""
    area = round(float(area))
    if area < 90:
        return "90㎡以下"
    elif 90 <= area < 105:
        return "90-105㎡"
    elif 105 <= area < 120:
        return "105-120㎡"
    elif 120 <= area < 140:
        return "120-140㎡"
    else:
        return "140㎡以上"

def load_data(file_path):
    """Load Excel data without headers"""
    try:
        # Read Excel file without headers
        df = pd.read_excel(file_path, header=None)
        
        # Set column names based on Chinese descriptions
        df.columns = ['供应时间', '预售证编号', '项目名称', '项目地址', '房间号', '物业类型', '户型', '面积']
        
        # Clean data - remove any rows with missing critical data
        df = df.dropna(subset=['物业类型', '户型', '面积'])
        
        # Convert area to numeric and round
        df['面积'] = pd.to_numeric(df['面积'], errors='coerce')
        df = df.dropna(subset=['面积'])
        df['面积'] = df['面积'].round()
        
        # Add area category
        df['面积段'] = df['面积'].apply(categorize_area)
        
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def analyze_data(df):
    """Perform comprehensive analysis of the data"""
    
    # Basic statistics
    total_units = len(df)
    print(f"总单元数: {total_units:,}")
    print("=" * 80)
    
    # Analysis by building type
    building_analysis = {}
    
    for building_type in df['物业类型'].unique():
        building_data = df[df['物业类型'] == building_type]
        building_total = len(building_data)
        
        # Room type analysis
        room_type_counts = building_data['户型'].value_counts()
        
        # Area range analysis
        area_range_counts = building_data['面积段'].value_counts()
        
        # Combined analysis: room type + area range
        combined_counts = building_data.groupby(['户型', '面积段']).size()
        
        building_analysis[building_type] = {
            '总单元数': building_total,
            '占比': f"{(building_total/total_units)*100:.2f}%",
            '户型种类数': len(room_type_counts),
            '面积段种类数': len(area_range_counts),
            '户型分布': room_type_counts.to_dict(),
            '面积段分布': area_range_counts.to_dict(),
            '户型_面积段组合': combined_counts.to_dict()
        }
    
    return building_analysis

def print_detailed_analysis(analysis, total_units):
    """Print detailed analysis results"""
    
    print("\n详细分析报告")
    print("=" * 80)
    
    for building_type, data in analysis.items():
        print(f"\n【{building_type}】")
        print(f"总单元数: {data['总单元数']:,} ({data['占比']})")
        print(f"户型种类数: {data['户型种类数']}")
        print(f"面积段种类数: {data['面积段种类数']}")
        
        print("\n户型分布:")
        for room_type, count in sorted(data['户型分布'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / data['总单元数']) * 100
            print(f"  {room_type}: {count:,}单元 ({percentage:.1f}%)")
        
        print("\n面积段分布:")
        for area_range, count in sorted(data['面积段分布'].items(), key=lambda x: x[1], reverse=True):
            percentage = (count / data['总单元数']) * 100
            print(f"  {area_range}: {count:,}单元 ({percentage:.1f}%)")
        
        print("\n户型-面积段组合:")
        combined_sorted = sorted(data['户型_面积段组合'].items(), key=lambda x: x[1], reverse=True)
        for (room_type, area_range), count in combined_sorted[:10]:  # Top 10 combinations
            percentage = (count / total_units) * 100
            print(f"  {room_type} + {area_range}: {count:,}单元 ({percentage:.2f}%)")
        
        print("-" * 80)

def generate_summary_report(df, analysis):
    """Generate a summary report"""
    
    print("\n项目总体分析摘要")
    print("=" * 80)
    
    # Overall area statistics
    print("\n面积统计:")
    print(f"最小面积: {df['面积'].min():.0f}㎡")
    print(f"最大面积: {df['面积'].max():.0f}㎡")
    print(f"平均面积: {df['面积'].mean():.0f}㎡")
    print(f"中位数面积: {df['面积'].median():.0f}㎡")
    
    # Overall area distribution
    print("\n整体面积段分布:")
    overall_area_dist = df['面积段'].value_counts()
    for area_range, count in overall_area_dist.items():
        percentage = (count / len(df)) * 100
        print(f"  {area_range}: {count:,}单元 ({percentage:.1f}%)")
    
    # Building type summary
    print("\n物业类型汇总:")
    building_summary = []
    for building_type, data in analysis.items():
        building_summary.append({
            '物业类型': building_type,
            '单元数': data['总单元数'],
            '占比': data['占比'],
            '户型数': data['户型种类数'],
            '面积段数': data['面积段种类数']
        })
    
    summary_df = pd.DataFrame(building_summary)
    print(summary_df.to_string(index=False))

def run(project_name: str, file_path: str = "resources/working_data/all_supply_with_date_data.xlsx") -> Dict[str, Any]:
    """Run the supply data analysis with a given project name and file path."""
    
    # File path
    file_path = Path(file_path)
    
    if not file_path.exists():
        print(f"文件不存在: {file_path}")
        return {}
    
    print("开始分析房地产供应数据...")
    print("=" * 80)
    
    # Load data
    df = load_data(file_path)
    if df is None:
        return {}
    
    print(f"成功加载数据，共{len(df)}条记录")
    
    # Get current date in YYYYMMDD format
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Create output directory
    output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze data
    analysis = analyze_data(df)
    
    # Generate reports
    generate_summary_report(df, analysis)
    print_detailed_analysis(analysis, len(df))
    
    # Save detailed results to Excel
    output_path = output_dir / f"{project_name}_供应明细表.xlsx"
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Summary sheet
        summary_data = []
        for building_type, data in analysis.items():
            for (room_type, area_range), count in data['户型_面积段组合'].items():
                summary_data.append({
                    '物业类型': building_type,
                    '户型': room_type,
                    '面积段': area_range,
                    '单元数': count,
                    '占总项目比例': f"{(count/len(df))*100:.2f}%",
                    '占该类型比例': f"{(count/data['总单元数'])*100:.2f}%"
                })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='详细分析结果', index=False)
        
        # Overall statistics
        overall_stats = pd.DataFrame({
            '统计项': ['总单元数', '最小面积', '最大面积', '平均面积', '中位数面积'],
            '数值': [len(df), df['面积'].min(), df['面积'].max(), 
                    df['面积'].mean(), df['面积'].median()]
        })
        overall_stats.to_excel(writer, sheet_name='总体统计', index=False)
    
    print(f"\n详细分析结果已保存至: {output_path}")
    
    return {
        'analysis': analysis,
        'total_units': len(df),
        'overall_stats': {
            '最小面积': df['面积'].min(),
            '最大面积': df['面积'].max(),
            '平均面积': df['面积'].mean(),
            '中位数面积': df['面积'].median()
        },
        'area_distribution': df['面积段'].value_counts().to_dict()
    }

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n分析结果:", result)