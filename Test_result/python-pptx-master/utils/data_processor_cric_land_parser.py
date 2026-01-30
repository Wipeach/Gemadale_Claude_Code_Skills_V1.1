#!/usr/bin/env python3
"""
CRIC Land Data Parser

This module parses land parcel data from CRIC (China Real Estate Information Corporation)
crawled from web pages. The data has a specific structure with multiple sections that
need to be parsed separately to maintain data integrity.
"""

import json
import re
from typing import Dict, List, Any, Union
from datetime import datetime
from pathlib import Path

class CRICLandParser:
    """Parser for CRIC land parcel data files."""
    
    def __init__(self):
        self.sections = [
            "基本信息:", "上市信息：", "成交信息:", "标书文件:"
        ]
    
    def read_file(self, file_path: str) -> List[str]:
        """Read the file and return lines as a list."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return [line.strip() for line in file.readlines()]
        except UnicodeDecodeError:
            # Try with different encoding if utf-8 fails
            with open(file_path, 'r', encoding='gb2312') as file:
                return [line.strip() for line in file.readlines()]
    
    def extract_section(self, lines: List[str], start_label: str, end_label: str = None) -> List[str]:
        """Extract content for a specific section."""
        try:
            start_idx = next(i for i, line in enumerate(lines) if start_label in line)
            if end_label:
                try:
                    end_idx = next(i for i in range(start_idx + 1, len(lines)) 
                                 if end_label in lines[i])
                    return lines[start_idx + 1:end_idx]
                except StopIteration:
                    return lines[start_idx + 1:]
            else:
                # Find next section or end of file
                next_sections = [s for s in self.sections if s != start_label]
                end_idx = len(lines)
                for section in next_sections:
                    try:
                        idx = next(i for i in range(start_idx + 1, len(lines)) 
                                 if section in lines[i])
                        end_idx = min(end_idx, idx)
                    except StopIteration:
                        continue
                return lines[start_idx + 1:end_idx]
        except StopIteration:
            return []
    
    def parse_key_value_pairs(self, lines: List[str]) -> Dict[str, Any]:
        """Parse key-value pairs from lines of text."""
        result = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line == "更多":
                i += 1
                continue
            
            # Check if line contains "信息:" or "：" (section header)
            if line.endswith((":", "：")) and any(section in line for section in self.sections):
                i += 1
                continue
            
            # Handle colon-separated key-value pairs on same line
            if ":" in line or "：" in line:
                colon_pos = line.find(":") if ":" in line else line.find("：")
                key = line[:colon_pos].strip()
                value = line[colon_pos + 1:].strip()
                if key and value:
                    result[key] = value
                    i += 1
                    continue
            
            # Handle key on one line, value on next line(s)
            key = line
            i += 1
            value_parts = []
            
            while i < len(lines):
                next_line = lines[i].strip()
                if not next_line:
                    i += 1
                    continue
                
                # Check if next line is a key for a new pair
                if (next_line.endswith((":", "：")) or 
                    (not next_line.startswith((" ", "\t", "    "))) and
                    (not any(char in next_line for char in [":", "："])) and
                    self._line_looks_like_key(next_line)):
                    break
                
                value_parts.append(next_line)
                i += 1
            
            if value_parts:
                result[key] = " ".join(value_parts)
            elif key:
                result[key] = ""
        
        return self._clean_key_value_result(result)
    
    def _line_looks_like_key(self, line: str) -> bool:
        """Determine if a line looks like a key rather than value."""
        # Keys are typically short and don't contain Chinese punctuation
        if len(line) > 15:
            return False
        key_indicators = [":", "：", "数", "率", "比", "费", "址", "期", "色", "型", "价", "积", "率", "限", "年"]
        return any(indicator in line for indicator in key_indicators)
    
    def _clean_key_value_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Clean the key-value pairs result."""
        cleaned = {}
        for key, value in result.items():
            if isinstance(value, str):
                value = value.strip()
                if value == "" or value == "-":
                    continue
            cleaned[key] = value
        return cleaned
    
    def parse_general_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse the general land parcel information above the first section."""
        general_info = {}
        
        # Look for lines between "功能导航" and "基本信息:"
        try:
            func_nav_idx = next(i for i, line in enumerate(lines) if "功能导航" in line)
            basic_info_idx = next(i for i, line in enumerate(lines) if "基本信息:" in line)
            
            relevant_lines = lines[func_nav_idx + 1:basic_info_idx]
            
            # Parse the land attributes line
            for line in relevant_lines:
                line = line.strip()
                if not line or "项目详情" in line or "住宅" in line or "土地" in line:
                    continue
                
                # Handle key-value pairs in the format: 土地属性：住宅... 成交总价：643,500万元...
                if "土地属性" in line and "成交总价" in line:
                    # This is the main info line with multiple key-value pairs
                    parts = line.split(' ')
                    
                    # Define expected keys to extract
                    general_keys = [
                        "土地属性", "成交总价", "楼板价", "出让底价", 
                        "溢价率", "总建面积", "建设用地（净用地）", 
                        "受让方", "开发商"
                    ]
                    
                    # Parse key-value pairs from the concatenated string
                    current_key = None
                    remaining_text = line
                    
                    for key in general_keys:
                        if key in remaining_text:
                            key_start = remaining_text.find(key)
                            rest = remaining_text[key_start + len(key):]
                            
                            # Find value - it ends when next key starts or at end
                            next_key_pos = len(rest)
                            for next_key in general_keys:
                                if next_key != key and next_key in rest:
                                    next_key_pos = min(next_key_pos, rest.find(next_key))
                            
                            value = rest[:next_key_pos].strip().lstrip('：').strip()
                            
                            # Clean up spacing issues
                            value = value.split(' ')[0] if ' ' in value and len(value.split(' ')) > 1 and any(kw in ' '.join(value.split(' ')[1:]) for kw in general_keys) else value
                            
                            general_info[key] = value
                            remaining_text = rest[next_key_pos:]
                    
                # Handle developer info
                elif "受让方" in line or "开发商" in line:
                    if "受让方" in line:
                        value = line.split("受让方：")[1].split("开发商")[0].strip()
                        general_info["受让方"] = value.strip("; ")
                    
                    if "开发商" in line:
                        try:
                            value = line.split("开发商：")[1].strip()
                            general_info["开发商"] = value.strip("; ")
                        except IndexError:
                            pass
                            
        except StopIteration:
            pass
        
        return general_info
    
    def parse_basic_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse basic information section with fine-grained key extraction."""
        section_lines = self.extract_section(lines, "基本信息:")
        
        # Define the exact keys we expect in the basic info section
        basic_info_keys = [
            "所属城市", "所在区域", "板块", "环线位置", "土地属性", 
            "土地用途", "土地用途（特殊）", "土地现状", "总建面积", 
            "用地面积", "建设用地（净用地）", "绿化率", "容积率", 
            "使用年限", "建筑限高", "土地地址", "项目四至"
        ]
        
        result = {}
        
        # First, try direct key-value mapping on separate lines
        current_key = None
        i = 0
        
        while i < len(section_lines):
            line = section_lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this is a key
            found_key = None
            for expected_key in basic_info_keys:
                if line == expected_key:
                    found_key = expected_key
                    break
            
            if found_key:
                # This is a key, collect the next non-empty line as value
                current_key = found_key
                i += 1
                
                while i < len(section_lines):
                    value_line = section_lines[i].strip()
                    if value_line and value_line not in basic_info_keys:
                        result[current_key] = value_line
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        
        # Handle missing keys by processing the entire text
        self._extract_missing_basic_info(section_lines, result, basic_info_keys)
        
        return result
    
    def _extract_missing_basic_info(self, lines: List[str], result: Dict[str, Any], expected_keys: List[str]) -> None:
        """Extract any missing basic info keys from the raw text."""
        text = "\n".join(lines)
        
        # Create comprehensive patterns for key-value extraction
        for key in expected_keys:
            if key not in result or not result[key].strip():
                # Look for key on its own line followed by value on next line
                pattern = r"{}\n\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and not any(k in value for k in expected_keys):
                        result[key] = value
                else:
                    # Look for key:value format
                    pattern = r"{}[:：]\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                    match = re.search(pattern, text, re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            result[key] = value
    
    def parse_listing_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse listing/market information section."""
        section_lines = self.extract_section(lines, "上市信息：")
        
        # Define the exact keys we expect in the listing info section
        listing_info_keys = [
            "公告号/宗地编号", "出让方式", "详细出让方式", "公告时间", 
            "报名时间", "挂牌时间", "文件领取时间", "保证金到账时间", 
            "出让底价", "出让楼板价", "出让每亩地价", "最小增幅度", 
            "竞买保证金", "联系电话", "联系地址", "交易地址", "查询网址"
        ]
        
        result = {}
        
        # First, try direct key-value mapping on separate lines
        current_key = None
        i = 0
        
        while i < len(section_lines):
            line = section_lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this is a key
            found_key = None
            for expected_key in listing_info_keys:
                if line == expected_key:
                    found_key = expected_key
                    break
            
            if found_key:
                # This is a key, collect the next non-empty line as value
                current_key = found_key
                i += 1
                
                while i < len(section_lines):
                    value_line = section_lines[i].strip()
                    if value_line and value_line not in listing_info_keys:
                        result[current_key] = value_line
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        
        # Handle missing keys by processing the entire text
        self._extract_missing_listing_info(section_lines, result, listing_info_keys)
        
        return result
    
    def _extract_missing_listing_info(self, lines: List[str], result: Dict[str, Any], expected_keys: List[str]) -> None:
        """Extract any missing listing info keys from the raw text."""
        text = "\n".join(lines)
        
        # Create comprehensive patterns for key-value extraction
        for key in expected_keys:
            if key not in result or not result[key].strip():
                # Look for key on its own line followed by value on next line
                pattern = r"{}\n\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and not any(k in value for k in expected_keys):
                        result[key] = value
                else:
                    # Look for key:value format
                    pattern = r"{}[:：]\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                    match = re.search(pattern, text, re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            result[key] = value
    
    def parse_transaction_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse transaction information section."""
        section_lines = self.extract_section(lines, "成交信息:")
        
        # Define the exact keys we expect in the transaction info section
        transaction_info_keys = [
            "成交现状", "成交时间", "成交总价", "楼板价", "每亩地价", 
            "溢价率", "自持比例", "受让方", "开发商", "项目开发商"
        ]
        
        result = {}
        
        # First, try direct key-value mapping on separate lines
        current_key = None
        i = 0
        
        while i < len(section_lines):
            line = section_lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this is a key
            found_key = None
            for expected_key in transaction_info_keys:
                if line == expected_key:
                    found_key = expected_key
                    break
            
            if found_key:
                # This is a key, collect the next non-empty line as value
                current_key = found_key
                i += 1
                
                while i < len(section_lines):
                    value_line = section_lines[i].strip()
                    if value_line and value_line not in transaction_info_keys:
                        result[current_key] = value_line
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        
        # Handle missing keys by processing the entire text
        self._extract_missing_transaction_info(section_lines, result, transaction_info_keys)
        
        return result
    
    def _extract_missing_transaction_info(self, lines: List[str], result: Dict[str, Any], expected_keys: List[str]) -> None:
        """Extract any missing transaction info keys from the raw text."""
        text = "\n".join(lines)
        
        # Create comprehensive patterns for key-value extraction
        for key in expected_keys:
            if key not in result or not result[key].strip():
                # Look for key on its own line followed by value on next line
                pattern = r"{}\n\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and not any(k in value for k in expected_keys):
                        result[key] = value
                else:
                    # Look for key:value format
                    pattern = r"{}[:：]\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                    match = re.search(pattern, text, re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            result[key] = value
    
    def parse_tender_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse tender/bid document section."""
        section_lines = self.extract_section(lines, "标书文件:")
        
        # Define the exact keys we expect in the tender info section
        tender_info_keys = [
            "规划意见", "招标/挂牌/拍卖公告"
        ]
        
        result = {}
        
        # First, try direct key-value mapping on separate lines
        current_key = None
        i = 0
        
        while i < len(section_lines):
            line = section_lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this is a key
            found_key = None
            for expected_key in tender_info_keys:
                if line == expected_key:
                    found_key = expected_key
                    break
            
            if found_key:
                # This is a key, collect the next non-empty line as value
                current_key = found_key
                i += 1
                
                while i < len(section_lines):
                    value_line = section_lines[i].strip()
                    if value_line and value_line not in tender_info_keys:
                        result[current_key] = value_line
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        
        # Handle missing keys by processing the entire text
        self._extract_missing_tender_info(section_lines, result, tender_info_keys)
        
        return result
    
    def _extract_missing_tender_info(self, lines: List[str], result: Dict[str, Any], expected_keys: List[str]) -> None:
        """Extract any missing tender info keys from the raw text."""
        text = "\n".join(lines)
        
        # Create comprehensive patterns for key-value extraction
        for key in expected_keys:
            if key not in result or not result[key].strip():
                # Look for key on its own line followed by value on next line
                pattern = r"{}\n\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                match = re.search(pattern, text, re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and not any(k in value for k in expected_keys):
                        result[key] = value
                else:
                    # Look for key:value format
                    pattern = r"{}[:：]\s*([^\n]+?)(?=\n|$)".format(re.escape(key))
                    match = re.search(pattern, text, re.MULTILINE)
                    if match:
                        value = match.group(1).strip()
                        if value:
                            result[key] = value
    
    def parse_all_sections(self, file_path: str) -> Dict[str, Any]:
        """Parse all sections from the file."""
        lines = self.read_file(file_path)
        
        result = {
            "土地概要信息": self.parse_general_info(lines),
            "基本信息": self.parse_basic_info(lines),
            "上市信息": self.parse_listing_info(lines),
            "成交信息": self.parse_transaction_info(lines),
            "标书文件": self.parse_tender_info(lines)
        }
        
        return result
    
    def save_json(self, result: Dict[str, Any], output_path: str):
        """Save parsed result to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

def run(project_name: str, file_path: str = "resources/working_data/test_log_land.txt") -> Dict[str, Any]:
    """Run the parser with a given project name and file path."""
    parser = CRICLandParser()
    
    # Parse the land data
    result = parser.parse_all_sections(file_path)
    
    # Define timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Create output directory
    output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    output_path = output_dir / f"{project_name}_土地基本信息.json"
    parser.save_json(result, output_path)
    
    print(f"Parsing completed! Results saved to {output_path}")
    
    return result

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n土地概要信息 section:")
    print(json.dumps(result["土地概要信息"], ensure_ascii=False, indent=2))
    print("\n成交信息 section:")
    print(json.dumps(result["成交信息"], ensure_ascii=False, indent=2))