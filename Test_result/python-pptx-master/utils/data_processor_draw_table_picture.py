# -*- coding: utf-8 -*-
"""
Real Estate Deal Data Visualization Script
Generates a combined bar, line, and table visualization from deal analysis results
"""

import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from matplotlib import colors as mcolors
from decimal import Decimal, ROUND_HALF_UP
import os
import math
import re
from collections import OrderedDict
import colorsys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

def run(project_name: str, file_path: str = None) -> Dict[str, Any]:
    """Run the deal data visualization with a given project name and file path."""
    
    # 字体与显示设置
    matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Noto Sans CJK SC']
    matplotlib.rcParams['axes.unicode_minus'] = False
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # 默认输入文件路径
    if file_path is None:
        file_path = f"resources/working_data/{project_name}_{timestamp}/processed_data/{project_name}_成交分析结果.xlsx"
    
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"找不到输入文件: {file_path}")
        return {}
    
    # 读取数据
    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl")
    print("原始列名：", df.columns.tolist())
    
    # ---------- 工具函数 ----------
    def find_col_by_keywords(df, keywords):
        for kw in keywords:
            if kw in df.columns:
                return kw
        for kw in keywords:
            for c in df.columns:
                if kw in str(c):
                    return c
        return None
    
    def _convert_price_label(lbl):
        s = str(lbl)
        s = re.sub(r'/\s*m2', '/㎡', s, flags=re.IGNORECASE)
        s = re.sub(r'/\s*m²', '/㎡', s, flags=re.IGNORECASE)
        s = s.replace('m2', '㎡').replace('m²', '㎡')
        if re.search(r'元', s) and re.search(r'㎡|m', s):
            s = s.replace('元', '万')
        s = re.sub(r'万\s*/\s*㎡', '万/㎡', s)
        return s
    
    def round_half_up_str(val):
        if pd.isna(val):
            return '0'
        try:
            num = float(str(val).replace(',', ''))
        except Exception:
            return '0'
        if not np.isfinite(num):
            return '0'
        return str(int(Decimal(str(num)).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
    
    def format_price_wan_str(val):
        if pd.isna(val):
            return '0.00'
        try:
            f = float(val) / 10000.0
        except Exception:
            return '0.00'
        return f"{f:.2f}"
    
    def extract_type_from_col(col_name):
        s = str(col_name)
        s = re.sub(r'\(.*?\)|（.*?）|\[.*?\]', '', s)
        tokens = ['成交套数','套数','套','成交均价','成交价','均价','单价','价格','元/㎡','元/平','元/平方米','元','/㎡','㎡','m2','m²']
        for tk in tokens:
            s = re.sub(re.escape(tk), ' ', s, flags=re.I)
        s = re.sub(r'[-_:：/\\]', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        if not s:
            m = re.search(r'(高层|低层|别墅|叠加|普通住宅|洋房|公寓|商铺|住宅)', str(col_name), flags=re.I)
            s = m.group(1) if m else str(col_name)
        return s
    
    def lighten_color(rgb, amount=0.4):
        h, l, s = colorsys.rgb_to_hls(*rgb)
        l = min(1, l + (1 - l) * amount)
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (r, g, b)
    
    def darken_color(rgb, amount=0.25):
        h, l, s = colorsys.rgb_to_hls(*rgb)
        l = max(0, l * (1 - amount))
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        return (r, g, b)
    
    # ---------- 时间列识别与补全 ----------
    time_col = find_col_by_keywords(df, ['时间']) or df.columns[0]
    _time_series = pd.to_datetime(df[time_col], format='%Y-%m', errors='coerce')
    if _time_series.isna().all():
        _time_series = pd.to_datetime(df[time_col], errors='coerce')
    if _time_series.isna().all():
        print("时间列解析失败：无法识别任何有效日期。")
        return {}
    min_date = _time_series.dropna().min().to_period('M').to_timestamp()
    last_date = _time_series.dropna().max().to_period('M').to_timestamp()
    print(f"[DEBUG] 原始数据时间范围: {min_date.strftime('%Y-%m')} 至 {last_date.strftime('%Y-%m')}")
    full_months = pd.date_range(start=min_date, end=last_date, freq='MS').strftime('%Y-%m').tolist()
    df[time_col] = _time_series.dt.to_period('M').dt.to_timestamp().dt.strftime('%Y-%m')
    full_df = pd.DataFrame({time_col: full_months}).merge(df, on=time_col, how='left')
    
    # ---------- 动态识别「套数」与「价格」列 ----------
    count_keywords = ['成交套数', '套数', '套']
    price_keywords_regex = r'均价|成交价|单价|元/㎡|元/平|元/平方米|元/㎡|元'
    price_cols = [c for c in df.columns if c != time_col and re.search(price_keywords_regex, str(c), flags=re.I)]
    price_map = OrderedDict()
    for c in price_cols:
        t = extract_type_from_col(c)
        if t not in price_map:
            price_map[t] = c
    
    count_cols_initial = [c for c in df.columns if c != time_col and any(kw in str(c) for kw in count_keywords)]
    count_map = OrderedDict()
    for c in count_cols_initial:
        t = extract_type_from_col(c)
        if t not in count_map:
            count_map[t] = c
    
    other_candidate_cols = [c for c in df.columns if c != time_col and c not in price_cols and c not in count_cols_initial]
    for c in other_candidate_cols:
        t = extract_type_from_col(c)
        assigned = False
        if t in price_map and t not in count_map:
            count_map[t] = c
            assigned = True
        if not assigned:
            try:
                s = pd.to_numeric(full_df[c], errors='coerce').dropna()
                if not s.empty:
                    frac_close = ((s - s.round()).abs() < 1e-6).mean()
                    if frac_close > 0.9 and s.max() < 1_000_000:
                        name_for_type = t if t else c
                        if name_for_type not in count_map:
                            count_map[name_for_type] = c
            except Exception:
                pass
    
    print("[DEBUG] 识别到的套数列:", count_map)
    print("[DEBUG] 识别到的价格列:", price_map)
    
    # ---------- 数值化（套数填 0；价格保留 NaN 以便判断是否有观测） ----------
    for col in count_map.values():
        if col in full_df.columns:
            full_df[col] = pd.to_numeric(full_df[col], errors='coerce').fillna(0).astype('int64')
    for col in price_map.values():
        if col in full_df.columns:
            full_df[col] = pd.to_numeric(full_df[col], errors='coerce')
    
    # ---------- display_df：用于表格显示（所有价格 NaN -> 0） ----------
    display_df = full_df.copy()
    price_cols_all = [c for c in price_map.values() if c in display_df.columns]
    if price_cols_all:
        display_df[price_cols_all] = display_df[price_cols_all].fillna(0)
    
    # ---------- 横轴标签 ----------
    cats = display_df[time_col].astype(str).tolist()
    x_labels = []
    for cat in cats:
        try:
            year, month = cat.split('-')
            month_int = int(month)
            if month_int == 1:
                x_labels.append(f'{year}-01')
            else:
                x_labels.append(f'{month_int:02d}')
        except Exception:
            x_labels.append(cat)
    x = np.arange(len(cats))
    
    # ---------- 颜色 ----------
    types_all = list(dict.fromkeys(list(count_map.keys()) + list(price_map.keys())))
    n_types = max(1, len(types_all))
    base_palette = sns.color_palette("tab10", n_types) if n_types <= 10 else sns.color_palette("tab20", n_types)
    type_color_dict = {}
    for i, t in enumerate(types_all):
        base = base_palette[i % len(base_palette)]
        bar_color = darken_color(base, amount=0.28)
        line_color = lighten_color(base, amount=0.45)
        type_color_dict[t] = {"base": base, "bar": bar_color, "line": line_color}
    
    # ---------- 表格分块参数 ----------
    CHUNK_SIZE = 25
    n_months = len(cats)
    n_chunks = max(1, math.ceil(n_months / CHUNK_SIZE))
    chart_h = 4.0
    spacer_h = 0.4
    table_h_per_chunk = 0.8
    
    # 用 constrained_layout 自动布局
    fig_h_total = chart_h + spacer_h + n_chunks * table_h_per_chunk + (n_chunks - 1) * 0.6
    fig = plt.figure(figsize=(20, fig_h_total), layout="constrained")
    gs = fig.add_gridspec(n_chunks + 2, 1,
                          height_ratios=[chart_h, spacer_h] + [table_h_per_chunk] * n_chunks)
    
    # ---------- 主图 ----------
    ax = fig.add_subplot(gs[0])
    n_bar_types = len(count_map)
    if n_bar_types > 0:
        total_bar_width = 0.78
        bar_w = total_bar_width / max(1, n_bar_types)
        offsets = (np.arange(n_bar_types) - (n_bar_types - 1) / 2) * bar_w
        for i, (t, col) in enumerate(count_map.items()):
            vals = display_df[col].fillna(0).astype(int).values
            bar_color = type_color_dict.get(t, {}).get("bar", None)
            ax.bar(x + offsets[i], vals, bar_w * 0.92, color=bar_color, alpha=0.96)
    
    # === 新增：把网格放到图层后面，并绘制淡灰色水平辅助线（不改变其他图形逻辑） ===
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color='#e6e6e6', linestyle='-', linewidth=0.8, alpha=0.9)
    # ==============================================================================
    
    ax.set_xticks(x)
    # === 修改：把横坐标刻度文字调大一些 ===
    ax.set_xticklabels(x_labels, rotation=90, ha='center', fontsize=14)
    # 修改纵坐标刻度大小
    ax.tick_params(axis='y', labelsize=14)
    ax.set_ylabel('成交套数 (套)', fontsize=16)  # 修改纵坐标标签大小
    
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    
    ax2 = ax.twinx()
    price_cols_with_observed = [c for c in price_map.values() if c in full_df.columns and full_df[c].notna().any()]
    if price_cols_with_observed:
        numeric_vals = display_df[price_cols_with_observed].astype(float) / 10000.0
        max_price = np.nanmax(numeric_vals.values)
        min_price = np.nanmin(numeric_vals.values)
        for t, col in price_map.items():
            if col in price_cols_with_observed:
                vals = display_df[col].astype(float) / 10000.0
                line_color = type_color_dict.get(t, {}).get("line", None)
                ax2.plot(x, vals, marker='o', linestyle='-', linewidth=1.6, markersize=5,
                         color=line_color, markerfacecolor='white', markeredgewidth=1.4, markeredgecolor=line_color)
        ax2.set_ylim(max(0.0, min_price * 0.88), max_price * 1.12)
    ax2.set_ylabel('成交均价 (万/㎡)', fontsize=16)  # 修改次坐标纵坐标标签大小
    ax2.tick_params(labelsize=14)  # 修改次坐标刻度大小
    
    # ---------- 表格 ----------
    df_t_full = display_df.set_index(time_col).T.copy()
    df_t_full.columns = df_t_full.columns.astype(str)
    row_order = list(count_map.values()) + list(price_map.values())
    df_t_full = df_t_full.reindex(row_order)
    
    row_labels_full = []
    for col in row_order:
        if col in count_map.values():
            t = next(k for k, v in count_map.items() if v == col)
            row_labels_full.append(f"{t} 成交套数(套)")
        else:
            t = next(k for k, v in price_map.items() if v == col)
            row_labels_full.append(_convert_price_label(f"{t} 成交均价 (元/㎡)"))
    
    price_row_indices = [i for i, col in enumerate(row_order) if col in price_map.values()]
    
    legend_color_map = {}
    for t in count_map.keys():
        legend_color_map[f"{t} 成交套数(套)"] = type_color_dict.get(t, {}).get("bar")
    for t in price_map.keys():
        legend_color_map[f"{t} 成交均价 (万/㎡)"] = type_color_dict.get(t, {}).get("line")
    
    for chunk_idx in range(n_chunks):
        start = chunk_idx * CHUNK_SIZE
        end = min((chunk_idx + 1) * CHUNK_SIZE, n_months)
        chunk_months = cats[start:end]
        display_months = x_labels[start:end]
        col_labels_chunk = [""] + display_months
        available_cols = [c for c in chunk_months if c in df_t_full.columns]
        if not available_cols:
            continue
    
        df_chunk_t = df_t_full[available_cols]
        cell_text = []
        for i in range(len(df_chunk_t)):
            row_label = row_labels_full[i]
            row_vals = []
            for c in df_chunk_t.columns:
                v = df_chunk_t.iloc[i][c]
                if (i in price_row_indices):
                    row_vals.append(format_price_wan_str(v))
                else:
                    row_vals.append(round_half_up_str(v))
            cell_text.append([row_label] + row_vals)
    
        ax_table = fig.add_subplot(gs[chunk_idx + 2])
        ax_table.axis('off')
        table = ax_table.table(cellText=cell_text,
                               colLabels=col_labels_chunk,
                               cellLoc='center',
                               loc='center')
    
        table.auto_set_font_size(False)
        # === 修改：放大表格字体（根据列数动态选择基准字号） ===
        base_font = 16
        if len(available_cols) > 20:
            base_font = 8.5
        elif len(available_cols) > 16:
            base_font = 9.5
        elif len(available_cols) > 12:
            base_font = 10.0
        else:
            base_font = 14
        table.set_fontsize(base_font)
        # 稍微增加纵向缩放以容纳更大的字体，但保持原有缩放思路
        table.scale(1, 0.9 + max(0, (len(available_cols) - 6) * 0.012))
        # ==============================================================================
    
        first_col_texts = [cell.get_text().get_text() 
                   for (r, c), cell in table.get_celld().items() if c == 0]
        max_chars = max(len(t) for t in first_col_texts) if first_col_texts else 6
        # 基准宽度随字数增加，每个字符大约 0.012 ~ 0.015
        first_col_width = max(0.08, min(0.25, max_chars * 0.014))

        for (r, c), cell in table.get_celld().items():
            if c == 0:
                cell.set_width(first_col_width)
    
        header_default_bg = "#f2f2f2"
        for j in range(len(col_labels_chunk)):
            if (0, j) in table.get_celld():
                hcell = table.get_celld()[(0, j)]
                hcell.set_facecolor(header_default_bg)
                hcell.get_text().set_weight("bold")
                # === 修改：表头字体也放大一点 ===
                hcell.get_text().set_fontsize(max(7, base_font + 1))
    
        for (r, c), cell in table.get_celld().items():
            if r == 0:
                continue
            # r-1 对应数据行索引（因为表格第一行为列头）
            if (r - 1) in price_row_indices:
                # 价格行略微使用相同或稍小字号，但总体放大
                cell.get_text().set_fontsize(max(7, base_font - 0))
            else:
                cell.get_text().set_fontsize(base_font)
    
        for row_idx, row_label in enumerate(row_labels_full):
            color = legend_color_map.get(row_label, None)
            if color is not None:
                cell_key = (row_idx + 1, 0)
                if cell_key in table.get_celld():
                    cell = table.get_celld()[cell_key]
                    try:
                        c_hex = mcolors.to_hex(color)
                    except Exception:
                        continue
                    cell.set_facecolor(c_hex)
                    cell.get_text().set_color('white')
                    cell.get_text().set_weight('bold')
    
    # 保存图片
    output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    out_img = output_dir / f"{project_name}_成交结果分析混合图与表.png"
    fig.savefig(out_img, dpi=300)
    plt.close(fig)
    print("已保存图片：", out_img)
    
    # 返回结果
    return {
        'output_image': str(out_img),
        'time_range': {
            'start': min_date.strftime('%Y-%m'),
            'end': last_date.strftime('%Y-%m')
        },
        'types': list(dict.fromkeys(list(count_map.keys()) + list(price_map.keys())))
    }

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n可视化结果:", result)
