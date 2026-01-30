
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract opening information from a text file and create an Excel table with Chinese column names and auto-adjusted column widths.
"""

import pandas as pd
import re
from datetime import datetime
import os
from pathlib import Path
from openpyxl import load_workbook

def run(project_name):
    """
    Extract opening information from a text file and save it to an Excel file with auto-adjusted column widths.

    Args:
        project_name (str): Name of the project.

    Returns:
        dict: Contains status and output file path or error message.
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    input_file = f"resources/working_data/{project_name}_{timestamp}/{project_name}_基本信息.txt"
    output_file = f"resources/working_data/{project_name}_{timestamp}/processed_data/{project_name}_开盘信息.xlsx"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"错误: 文件 {input_file} 未找到。")
        return {"status": "error", "message": f"文件 {input_file} 未找到"}
    except Exception as e:
        print(f"错误: 读取文件时出错: {e}")
        return {"status": "error", "message": f"读取文件时出错: {e}"}
    
    in_section = False
    current_date = None
    current_desc = []
    collecting_desc = False
    data = []
    
    for line in lines:
        line = line.strip()
        if line == "开盘信息:":
            in_section = True
            continue
        if not in_section:
            continue
        if line == "更多":
            break
        if re.match(r'^\d{4}/\d{2}/\d{2}$', line):
            if current_date and current_desc:
                desc = ' '.join(current_desc).strip()
                row = {}
                
                # Parse batch
                batch_match = re.search(r'(第.*?批|住宅,.*?批)', desc)
                row['批次'] = batch_match.group(1).replace('住宅,', '').strip() if batch_match else '-'
                
                # Total sets
                total_sets_match = re.search(r'共(\d+)套', desc)
                row['总套数'] = int(total_sets_match.group(1)) if total_sets_match else '-'
                
                # Small high sets
                small_high_sets_match = re.search(r'(?:多层、小高层|小高层)(\d+)套', desc)
                row['小高层套数'] = int(small_high_sets_match.group(1)) if small_high_sets_match else '-'
                
                # Overlay sets
                overlay_sets_match = re.search(r'叠加(\d+)套', desc)
                row['叠加套数'] = int(overlay_sets_match.group(1)) if overlay_sets_match else '-'
                
                # Small high price min max
                small_high_price_match = re.search(r'(?:多层、小高层|小高层).*价格(?:在)?(\d+)-(\d+)元/㎡', desc)
                if small_high_price_match:
                    row['小高层价格最低'] = int(small_high_price_match.group(1))
                    row['小高层价格最高'] = int(small_high_price_match.group(2))
                else:
                    row['小高层价格最低'] = '-'
                    row['小高层价格最高'] = '-'
                
                # Small high mean
                small_high_mean_match = re.search(r'(?:多层、小高层|小高层).*?(?:销售)?均价(?:为)?(\d+)元/㎡', desc)
                row['小高层均价'] = int(small_high_mean_match.group(1)) if small_high_mean_match else '-'
                
                # Overlay price min max
                overlay_price_match = re.search(r'(叠加|叠加别墅|别墅).*价格(?:在)?(\d+)-(\d+)元/㎡', desc)
                if overlay_price_match:
                    row['叠加价格最低'] = int(overlay_price_match.group(2))
                    row['叠加价格最高'] = int(overlay_price_match.group(3))
                else:
                    row['叠加价格最低'] = '-'
                    row['叠加价格最高'] = '-'
                
                # Overlay mean
                overlay_mean_match = re.search(r'(叠加|叠加别墅|别墅).*?(?:销售)?均价(?:为)?(\d+)元/㎡', desc)
                row['叠加均价'] = int(overlay_mean_match.group(2)) if overlay_mean_match else '-'
                
                # Whole mean
                whole_mean_match = re.search(r'(整盘|本批次整体)均价(?:为)?(\d+)元/㎡', desc)
                row['整体均价'] = int(whole_mean_match.group(2)) if whole_mean_match else '-'
                
                row['开盘日期'] = current_date
                data.append(row)
            current_date = line
            current_desc = []
            collecting_desc = False
            continue
        if line == "开盘描述":
            collecting_desc = True
            continue
        if collecting_desc and ("查看产品信息" in line or "查看销售报价" in line):
            collecting_desc = False
            continue
        if collecting_desc and line:
            current_desc.append(line + ' ')
    
    # Add the last entry
    if current_date and current_desc:
        desc = ' '.join(current_desc).strip()
        row = {}
        
        batch_match = re.search(r'(第.*?批|住宅,.*?批)', desc)
        row['批次'] = batch_match.group(1).replace('住宅,', '').strip() if batch_match else '-'
        
        total_sets_match = re.search(r'共(\d+)套', desc)
        row['总套数'] = int(total_sets_match.group(1)) if total_sets_match else '-'
        
        small_high_sets_match = re.search(r'(?:多层、小高层|小高层)(\d+)套', desc)
        row['小高层套数'] = int(small_high_sets_match.group(1)) if small_high_sets_match else '-'
        
        overlay_sets_match = re.search(r'叠加(\d+)套', desc)
        row['叠加套数'] = int(overlay_sets_match.group(1)) if overlay_sets_match else '-'
        
        small_high_price_match = re.search(r'(?:多层、小高层|小高层).*价格(?:在)?(\d+)-(\d+)元/㎡', desc)
        if small_high_price_match:
            row['小高层价格最低'] = int(small_high_price_match.group(1))
            row['小高层价格最高'] = int(small_high_price_match.group(2))
        else:
            row['小高层价格最低'] = '-'
            row['小高层价格最高'] = '-'
        
        small_high_mean_match = re.search(r'(?:多层、小高层|小高层).*?(?:销售)?均价(?:为)?(\d+)元/㎡', desc)
        row['小高层均价'] = int(small_high_mean_match.group(1)) if small_high_mean_match else '-'
        
        overlay_price_match = re.search(r'(叠加|叠加别墅|别墅).*价格(?:在)?(\d+)-(\d+)元/㎡', desc)
        if overlay_price_match:
            row['叠加价格最低'] = int(overlay_price_match.group(2))
            row['叠加价格最高'] = int(overlay_price_match.group(3))
        else:
            row['叠加价格最低'] = '-'
            row['叠加价格最高'] = '-'
        
        overlay_mean_match = re.search(r'(叠加|叠加别墅|别墅).*?(?:销售)?均价(?:为)?(\d+)元/㎡', desc)
        row['叠加均价'] = int(overlay_mean_match.group(2)) if overlay_mean_match else '-'
        
        whole_mean_match = re.search(r'(整盘|本批次整体)均价(?:为)?(\d+)元/㎡', desc)
        row['整体均价'] = int(whole_mean_match.group(2)) if whole_mean_match else '-'
        
        row['开盘日期'] = current_date
        data.append(row)
    
    if not data:
        print("未找到开盘信息。")
        return {"status": "error", "message": "未找到开盘信息"}
    
    # Create DataFrame with specified column order
    columns = [
        '开盘日期', '批次', '总套数', '小高层套数', '小高层价格最低',
        '小高层价格最高', '小高层均价', '叠加套数',
        '叠加价格最低', '叠加价格最高', '叠加均价', '整体均价'
    ]
    df = pd.DataFrame(data, columns=columns)
    df = df.fillna('-')
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save to Excel
    try:
        df.to_excel(output_file, index=False, engine='openpyxl')
        
        # Adjust column widths
        wb = load_workbook(output_file)
        ws = wb.active
        
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # Get the column letter
            for cell in col:
                try:
                    # Convert cell value to string and calculate length (considering Chinese characters)
                    cell_value = str(cell.value)
                    cell_length = sum(2 if ord(c) > 127 else 1 for c in cell_value)
                    max_length = max(max_length, cell_length)
                except:
                    pass
            # Adjust width, adding padding and scaling for Chinese characters
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = min(adjusted_width, 50)  # Cap at 50 for readability
        
        wb.save(output_file)
        print(f"已将开盘信息保存至 {output_file}")
        return {"status": "success", "output_file": output_file}
    except Exception as e:
        print(f"保存 Excel 文件时出错: {e}")
        return {"status": "error", "message": f"保存 Excel 文件时出错: {e}"}

if __name__ == "__main__":
    result = run("华发四季半岛")
    print(result)
