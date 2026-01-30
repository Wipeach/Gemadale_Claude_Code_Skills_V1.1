#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解析 full.md 生成 report_data.json
用于金地投资报告网站生成
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict

@dataclass
class Block:
    """内容块"""
    type: str  # text, table, image, callout, list, gallery
    content: str = ""
    metadata: Dict = field(default_factory=dict)

@dataclass
class Section:
    """小节"""
    id: str
    title: str
    blocks: List[Block] = field(default_factory=list)
    key_takeaways: List[str] = field(default_factory=list)
    kpis: List[Dict] = field(default_factory=list)

@dataclass
class Part4Option:
    """Part4 方案"""
    option_id: str
    option_title: str
    source_pages: List[str] = field(default_factory=list)
    assets: Dict = field(default_factory=dict)
    summary: str = ""
    advantages: List[str] = field(default_factory=list)

@dataclass
class Part:
    """Part"""
    part_id: str
    title: str
    sections: List[Section] = field(default_factory=list)
    part4_options: Optional[List[Part4Option]] = None

@dataclass
class Report:
    """报告"""
    meta: Dict = field(default_factory=dict)
    parts: List[Part] = field(default_factory=list)

class ReportParser:
    """报告解析器"""

    def __init__(self, md_path: str, images_dir: str):
        self.md_path = Path(md_path)
        self.images_dir = Path(images_dir)
        self.lines: List[str] = []
        self.images: List[str] = []

    def load(self):
        """加载文件"""
        with open(self.md_path, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()

        # 加载图片列表
        if self.images_dir.exists():
            self.images = [f.name for f in self.images_dir.glob('*')
                          if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']]

    def parse(self) -> Report:
        """解析报告"""
        self.load()

        report = Report()

        # 提取元数据
        report.meta = self._extract_meta()

        # 第一步:识别所有Part的标题
        part_headers = []
        for i, line in enumerate(self.lines):
            line = line.rstrip()
            part_match = re.match(r'^(?:#\s+)?(PART\d+|Part\s*\d+)\s*(.+)', line, re.IGNORECASE)
            if part_match:
                part_label = part_match.group(1).upper()
                part_title = part_match.group(2).strip()
                part_headers.append({
                    'line_num': i,
                    'label': part_label,
                    'title': part_title
                })

        # 第二步:使用"# XX"标题将sections分配给对应Part
        current_part = None
        i = 0
        part_index = 0

        while i < len(self.lines):
            line = self.lines[i].rstrip()

            # 检测Part标题行 (初始化Part)
            part_match = re.match(r'^(?:#\s+)?(PART\d+|Part\s*\d+)\s*(.+)', line, re.IGNORECASE)
            if part_match:
                part_label = part_match.group(1).upper()
                part_title = part_match.group(2).strip()

                # 规范化part_id
                part_id_map = {
                    'PART1': 'part1', 'PART2': 'part2', 'PART3': 'part3',
                    'PART4': 'part4', 'PART5': 'part5', 'PART6': 'part6',
                }
                part_id = part_id_map.get(part_label.upper(), f'part{len(report.parts)+1}')

                current_part = Part(part_id=part_id, title=part_title)
                report.parts.append(current_part)
                part_index = len(report.parts) - 1

            # 检测 "# XX" 标题 (将section分配给当前Part)
            section_match = re.match(r'^#\s+(\d+|\d+\.\d+)\s+(.+)', line)
            if section_match and current_part:
                section_num = section_match.group(1)
                section_title = section_match.group(2).strip()
                section_id = f"section_{len(current_part.sections) + 1}_{hashlib.md5(section_title.encode()).hexdigest()[:8]}"

                section = Section(id=section_id, title=section_title)
                section.blocks = self._parse_blocks(i)

                # 检查section编号是否属于当前Part
                if '.' in section_num:
                    # 小节 (如 1.1) - 肯定属于当前Part
                    current_part.sections.append(section)
                else:
                    # 大节 (如 01, 02) - 需要判断是否切换到新Part
                    main_section_num = int(section_num)
                    target_part_index = main_section_num - 1  # 01->part1, 02->part2

                    if target_part_index < len(report.parts):
                        # 切换到对应的Part
                        current_part = report.parts[target_part_index]
                        current_part.sections.append(section)
                    elif target_part_index == len(report.parts):
                        # 这是下一个Part的第一个section
                        current_part.sections.append(section)
                    else:
                        # 如果已经超出现有Part范围,添加到最后一个
                        if report.parts:
                            report.parts[-1].sections.append(section)

            i += 1

        # Part4特殊处理:提取方案
        for part in report.parts:
            if part.part_id.lower() == 'part4':
                part.part4_options = self._extract_part4_options(part)

        return report

    def _extract_meta(self) -> Dict:
        """提取元数据"""
        meta = {
            'title': '投资分析报告',
            'source': self.md_path.stem
        }

        # 从第一行尝试提取项目名称
        if self.lines:
            first_line = self.lines[0].strip()
            if first_line and not first_line.startswith('#'):
                meta['project'] = first_line
            elif len(self.lines) > 1:
                second_line = self.lines[1].strip()
                if second_line.startswith('#'):
                    meta['project'] = second_line.lstrip('#').strip()

        return meta

    def _parse_part(self, part_label: str, part_title: str, start_line: int) -> Part:
        """解析一个Part"""
        # 规范化part_id
        part_id_map = {
            'PART1': 'part1', 'PART2': 'part2', 'PART3': 'part3',
            'PART4': 'part4', 'PART5': 'part5', 'PART6': 'part6',
        }
        for k, v in part_id_map.items():
            if k in part_label or k.lower() in part_label.lower():
                part_id = v
                break
        else:
            # 中文数字映射
            cn_num_map = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6'}
            for cn, num in cn_num_map.items():
                if cn in part_label:
                    part_id = f'part{num}'
                    break
            else:
                part_id = f'part{len(re.findall(r"[一二三四五六七八九十]", part_label)) + 1}'

        part = Part(part_id=part_id, title=part_title)
        part.sections = self._parse_sections(start_line)

        return part

    def _parse_sections(self, start_line: int) -> List[Section]:
        """解析小节"""
        sections = []
        current_section = None
        i = start_line + 1  # 跳过Part标题行

        while i < len(self.lines):
            line = self.lines[i].rstrip()

            # 检测Part结束 (下一个Part开始)
            if re.match(r'^(?:#\s+)?(PART\d+|Part\s*\d+)', line, re.IGNORECASE):
                break

            # 检测小节标题
            section_match = re.match(r'^#\s+([\d\.]+|[一二三四五六七八九十]+[、\.]?)\s*(.+)', line)
            if section_match:
                if current_section:
                    sections.append(current_section)

                section_num = section_match.group(1)
                section_title = section_match.group(2).strip()
                section_id = f"section_{len(sections) + 1}_{hashlib.md5(section_title.encode()).hexdigest()[:8]}"

                current_section = Section(id=section_id, title=section_title)
                current_section.blocks = self._parse_blocks(i)
            elif current_section:
                # 非标题行,作为文本块添加
                if line.strip():
                    current_section.blocks.append(Block(type='text', content=line))

            i += 1

        if current_section:
            sections.append(current_section)

        return sections

    def _parse_blocks(self, start_line: int) -> List[Block]:
        """解析内容块"""
        blocks = []
        i = start_line + 1

        while i < len(self.lines):
            line = self.lines[i].rstrip()

            # 检测标题,停止
            if line.startswith('#'):
                break

            # 检测图片
            img_match = re.match(r'!\[\]\(images/([^)]+)\)', line)
            if img_match:
                img_name = img_match.group(1)
                blocks.append(Block(type='image', content=img_name))
                i += 1
                continue

            # 检测HTML表格
            if '<table>' in line:
                table_lines = [line]
                i += 1
                while i < len(self.lines) and '</table>' not in self.lines[i]:
                    table_lines.append(self.lines[i].rstrip())
                    i += 1
                if i < len(self.lines):
                    table_lines.append(self.lines[i].rstrip())
                blocks.append(Block(type='table', content='\n'.join(table_lines)))
                i += 1
                continue

            # 检测列表
            if re.match(r'^[\s]*[-•●]\s+', line) or re.match(r'^[\s]*\d+[、.]\s+', line):
                list_items = [line]
                i += 1
                while i < len(self.lines):
                    next_line = self.lines[i].rstrip()
                    if not next_line.strip() or next_line.startswith('#') or '<table>' in next_line or '![](images/' in next_line:
                        break
                    if re.match(r'^[\s]*[-•●]\s+', next_line) or re.match(r'^[\s]*\d+[、.]\s+', next_line):
                        list_items.append(next_line)
                        i += 1
                    else:
                        break
                blocks.append(Block(type='list', content='\n'.join(list_items)))
                continue

            # 文本行
            if line.strip():
                blocks.append(Block(type='text', content=line))

            i += 1

        return blocks

    def _extract_part4_options(self, part: Part) -> List[Part4Option]:
        """提取Part4方案"""
        options = []
        option_pattern = re.compile(r'方案\s*([一二三四五六七八九十\d]+)|Option\s*([A-Z])|方案(\d+)', re.IGNORECASE)

        for section in part.sections:
            for block in section.blocks:
                if block.type == 'text':
                    match = option_pattern.search(block.content)
                    if match:
                        option_num = match.group(1) or match.group(2) or match.group(3)
                        option_title = f"方案{self._normalize_option_num(option_num)}"
                        option_id = f"option_{len(options) + 1}"

                        options.append(Part4Option(
                            option_id=option_id,
                            option_title=option_title,
                            source_pages=[section.id],
                            assets={'images': [], 'tables': [], 'models': []},
                            summary="",
                            advantages=[]
                        ))

        return options

    def _normalize_option_num(self, num: str) -> str:
        """规范化方案编号"""
        cn_num_map = {
            '一': '一', '二': '二', '三': '三', '四': '四', '五': '五',
            '六': '六', '七': '七', '八': '八', '九': '九', '十': '十'
        }
        if num in cn_num_map:
            return cn_num_map[num]
        if num.isdigit():
            int_num = int(num)
            cn_nums = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']
            if int_num <= 10:
                return cn_nums[int_num]
        return num

    def generate_key_takeaways(self, section: Section) -> List[str]:
        """生成关键要点"""
        takeaways = []

        # 从文本中提取关键信息
        for block in section.blocks:
            if block.type == 'text':
                content = block.content
                # 寻找包含关键词的句子
                keywords = ['优势', '特点', '重点', '核心', '关键', '主要', '建议']
                for kw in keywords:
                    if kw in content:
                        takeaways.append(content[:100] + '...' if len(content) > 100 else content)
                        break

        # 如果没有找到,返回默认占位
        if not takeaways:
            takeaways = [
                "本节关键要点待补充",
                "请参考详细内容了解相关信息",
                "更多细节请查看完整报告"
            ]

        return takeaways[:5]  # 最多5条

    def extract_kpis(self, part: Part) -> List[Dict]:
        """提取KPI指标 (优先Part1和Part6)"""
        kpis = []

        if part.part_id in ['part1', 'part6']:
            for section in part.sections:
                for block in section.blocks:
                    if block.type == 'table':
                        # 尝试从表格中提取数字指标
                        kpis.append({
                            'label': '关键指标',
                            'value': '详见表格',
                            'source': section.title
                        })

        return kpis

def main():
    """主函数"""
    base_dir = Path('Test_result/investment_report_minerU')
    md_path = base_dir / 'full.md'
    images_dir = base_dir / 'images'
    output_path = base_dir / 'report_data.json'

    parser = ReportParser(str(md_path), str(images_dir))
    report = parser.parse()

    # 生成key_takeaways和kpis
    for part in report.parts:
        for section in part.sections:
            section.key_takeaways = parser.generate_key_takeaways(section)
        kpis = parser.extract_kpis(part)
        if kpis:
            for section in part.sections:
                section.kpis = kpis

    # 转换为字典
    report_dict = {
        'meta': report.meta,
        'parts': []
    }

    for part in report.parts:
        part_dict = {
            'part_id': part.part_id,
            'title': part.title,
            'sections': []
        }

        for section in part.sections:
            section_dict = {
                'id': section.id,
                'title': section.title,
                'blocks': [],
                'key_takeaways': section.key_takeaways,
                'kpis': section.kpis
            }

            for block in section.blocks:
                block_dict = {
                    'type': block.type,
                    'content': block.content,
                    'metadata': block.metadata
                }
                section_dict['blocks'].append(block_dict)

            part_dict['sections'].append(section_dict)

        if part.part4_options:
            part_dict['part4_options'] = []
            for opt in part.part4_options:
                opt_dict = {
                    'option_id': opt.option_id,
                    'option_title': opt.option_title,
                    'source_pages': opt.source_pages,
                    'assets': opt.assets,
                    'summary': opt.summary,
                    'advantages': opt.advantages
                }
                part_dict['part4_options'].append(opt_dict)

        report_dict['parts'].append(part_dict)

    # 保存JSON
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, ensure_ascii=False, indent=2)

    print(f"[OK] Parsed: {output_path}")
    print(f"  - {len(report.parts)} parts")
    for part in report.parts:
        print(f"  - {part.part_id}: {len(part.sections)} sections")

if __name__ == '__main__':
    main()
