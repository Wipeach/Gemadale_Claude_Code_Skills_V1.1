#!/usr/bin/env python3
"""
CRIC Housing Data Parser

This module parses housing project data from CRIC (China Real Estate Information Corporation)
crawled from web pages. The data has a specific structure with multiple sections that
need to be parsed separately to maintain data integrity.
"""

import json
import re
from typing import Dict, List, Any, Union
from datetime import datetime
from pathlib import Path

class CRICHousingParser:
    """Parser for CRIC housing project data files."""
    
    def __init__(self):
        self.sections = [
            "基本信息:", "企业信息:", "产品综览:", "产品细节:", 
            "装修情况:", "预证信息:", "开盘信息:", "营销信息:", "住宅图片："
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
        key_indicators = [":", "：", "数", "率", "比", "费", "址", "期", "色", "型"]
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
    
    def parse_basic_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse basic information section with fine-grained key extraction."""
        section_lines = self.extract_section(lines, "基本信息:")
        
        # Define the exact keys we expect in the basic info section
        basic_info_keys = [
            "所属城市", "区域", "板块", "环线位置", "销售状态",
            "产权类型", "产权年限", "最早开工时间", "最早开盘时间",
            "最晚交房时间", "楼盘地址", "售楼处地址", "项目四至", "售楼处电话"
        ]
        
        result = {}
        key_value_patterns = [
            r"(所属城市)[:：]\s*(.+?)(?=\n|$)",
            r"(区域)[:：]\s*(.+?)(?=\n|$)",
            r"(板块)[:：]\s*(.+?)(?=\n|$)",
            r"(环线位置)[:：]\s*(.+?)(?=\n|$)",
            r"(销售状态)[:：]\s*(.+?)(?=\n|$)",
            r"(产权类型)[:：]\s*(.+?)(?=\n|$)",
            r"(产权年限)[:：]\s*(.+?)(?=\n|$)",
            r"(最早开工时间)[:：]\s*(.+?)(?=\n|$)",
            r"(最早开盘时间)[:：]\s*(.+?)(?=\n|$)",
            r"(最晚交房时间)[:：]\s*(.+?)(?=\n|$)",
            r"(楼盘地址)[:：]\s*(.+?)(?=\n|$)",
            r"(售楼处地址)[:：]\s*(.+?)(?=\n|$)",
            r"(项目四至)[:：]\s*(.+?)(?=\n|$)",
            r"(售楼处电话)[:：]\s*(.+?)(?=\n|$)"
        ]
        
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
    
    def parse_company_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse company information section with fine-grained key extraction."""
        section_lines = self.extract_section(lines, "企业信息:")
        
        # Define the exact keys we expect in the company info section
        company_info_keys = [
            "开发商", "项目开发商", "投资商", "销售代理", "物业管理"
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
            for expected_key in company_info_keys:
                if line == expected_key:
                    found_key = expected_key
                    break
            
            if found_key:
                # This is a key, collect the next non-empty line as value
                current_key = found_key
                i += 1
                
                while i < len(section_lines):
                    value_line = section_lines[i].strip()
                    if value_line and value_line not in company_info_keys:
                        result[current_key] = value_line
                        i += 1
                        break
                    i += 1
            else:
                i += 1
        
        # Handle missing keys by processing the entire text
        self._extract_missing_company_info(section_lines, result, company_info_keys)
        
        return result
    
    def _extract_missing_company_info(self, lines: List[str], result: Dict[str, Any], expected_keys: List[str]) -> None:
        """Extract any missing company info keys from the raw text."""
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
    
    def parse_product_overview(self, lines: List[str]) -> Dict[str, Any]:
        """Parse product overview section including building types with nested key-value structure."""
        section_lines = self.extract_section(lines, "产品综览:")
        
        # First parse regular key-value pairs
        parsed = self.parse_key_value_pairs(section_lines)
        
        # Handle building types with nested structure
        building_types = self._parse_building_types(section_lines)
        
        # Remove building-related keys from parsed overview and clean it
        building_keys = ["多层", "小高层", "叠加"]
        clean_overview = {k: v for k, v in parsed.items() if k not in building_keys}
        
        return {
            "overview": clean_overview,
            "building_types": building_types,
            "room_types": []
        }
    
    def _parse_building_types(self, lines: List[str]) -> Dict[str, Dict[str, str]]:
        """Parse building types with their nested key-value structure."""
        building_types = {}
        expected_buildings = ["多层", "小高层", "叠加"]
        building_attributes = ["楼栋数", "楼层数"]
        
        current_building = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a building type
            if line in expected_buildings:
                current_building = line
                building_types[current_building] = {}
            elif current_building:
                # Check if we've reached the end of building data
                if line == "图片采集中…":
                    current_building = None
                else:
                    # Check for building attributes with multiple format patterns
                    for attr in building_attributes:
                        if line.startswith(attr):
                            # Handle both "attr value" and "attr: value" formats
                            value = line[len(attr):].strip()
                            if value.startswith(" ") or value.startswith(":"):
                                value = value.lstrip(" :").strip()
                            if value:
                                building_types[current_building][attr] = value
                            break
        
        return building_types
    
    def parse_product_details(self, lines: List[str]) -> Dict[str, Any]:
        """Parse product details section."""
        section_lines = self.extract_section(lines, "产品细节:")
        return self.parse_key_value_pairs(section_lines)
    
    def parse_decoration_info(self, lines: List[str]) -> Dict[str, Any]:
        """Parse decoration information section."""
        section_lines = self.extract_section(lines, "装修情况:")
        parsed = self.parse_key_value_pairs(section_lines)
        
        # Organize by room type
        room_types = ["卧室", "厨房", "客厅", "卫生间"]
        organized = {}
        
        for room in room_types:
            if room in parsed:
                if room not in organized:
                    organized[room] = {}
                organized[room] = parsed[room]
        
        return {
            "general_info": {k: v for k, v in parsed.items() if k not in room_types},
            "room_details": organized
        }
    
    def parse_permit_info(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse permit information section."""
        section_lines = self.extract_section(lines, "预证信息:")
        
        permits = []
        current_permit = {}
        
        for line in section_lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for dates (YYYY/MM/DD format)
            if re.match(r'\d{4}/\d{2}/\d{2}', line):
                if current_permit:
                    permits.append(current_permit)
                current_permit = {"日期": line}
            elif "号" in line and "预字" in line:
                current_permit["许可证号"] = line
            else:
                key_value = line.split(":")
                if len(key_value) == 2:
                    key, value = key_value
                    key = key.strip()
                    value = value.strip()
                    
                    # Handle specific structure for permit data
                    if "三房" in key or "叠加" in key:
                        if "房型" not in current_permit:
                            current_permit["房型"] = {}
                        current_permit["房型"][key] = value
                    else:
                        current_permit[key] = value
        
        if current_permit:
            permits.append(current_permit)
        
        return permits
    
    def parse_marketing_info(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse marketing information section."""
        section_lines = self.extract_section(lines, "营销信息:")
        
        marketing_items = []
        current_item = {}
        
        for line in section_lines:
            line = line.strip()
            if not line or line == "更多":
                continue
            
            # Check for dates
            if re.match(r'\d{4}/\d{2}/\d{2}', line):
                if current_item:
                    marketing_items.append(current_item)
                current_item = {"日期": line}
            elif line.startswith("活动描述:"):
                current_item["活动描述"] = line[5:].strip()
            elif ":" in line:
                key, value = line.split(":", 1)
                current_item[key.strip()] = value.strip()
        
        if current_item:
            marketing_items.append(current_item)
        
        return marketing_items
    
    def parse_house_images(self, lines: List[str]) -> Dict[str, int]:
        """Parse house images section."""
        section_lines = self.extract_section(lines, "住宅图片：")
        
        images = {}
        for line in section_lines:
            line = line.strip()
            if not line or line == "更多":
                continue
            
            if " " in line:
                key, value = line.rsplit(" ", 1)
                try:
                    images[key] = int(value)
                except ValueError:
                    images[key] = value
        
        return images
    
    def parse_open_info(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse opening information section."""
        section_lines = self.extract_section(lines, "开盘信息:", "营销信息:")
        
        openings = []
        current_open = {}
        
        for line in section_lines:
            line = line.strip()
            if not line or line == "更多":
                continue
            
            # Check for dates
            if re.match(r'\d{4}/\d{2}/\d{2}', line):
                if current_open:
                    openings.append(current_open)
                current_open = {"日期": line}
            elif "号" in line and "预字" in line:
                current_open["许可证号"] = line
            elif line.startswith("开盘套数"):
                try:
                    current_open["开盘套数"] = int(line.replace("开盘套数", "").replace("套", "").strip())
                except ValueError:
                    current_open["开盘套数"] = line
            elif line.startswith("开盘面积"):
                current_open["开盘面积"] = line.replace("开盘面积", "").strip()
            elif ":" in line:
                key, value = line.split(":", 1)
                current_open[key.strip()] = value.strip()
            else:
                # Handle descriptive lines
                if "开盘描述" not in current_open:
                    current_open["开盘描述"] = []
                current_open["开盘描述"].append(line)
        
        if current_open:
            openings.append(current_open)
        
        return openings
    
    def _parse_numeric_value(self, value: str) -> Union[float, str]:
        """Parse numeric values from Chinese text."""
        if not isinstance(value, str):
            return value
        
        value = value.replace(',', '').strip()
        # Extract numbers with units
        match = re.search(r'([\d.]+)\s*([\u4e00-\u9fff]*)', value)
        if match:
            num_str, unit = match.groups()
            try:
                return float(num_str)
            except ValueError:
                return value
        return value
    
    def parse_all_sections(self, file_path: str) -> Dict[str, Any]:
        """Parse all sections from the file."""
        lines = self.read_file(file_path)
        
        result = {
            "基本信息": self.parse_basic_info(lines),
            "企业信息": self.parse_company_info(lines),
            "产品综览": self.parse_product_overview(lines),
            "产品细节": self.parse_product_details(lines),
            "装修情况": self.parse_decoration_info(lines),
            "预证信息": self.parse_permit_info(lines),
            "开盘信息": self.parse_open_info(lines),
            "营销信息": self.parse_marketing_info(lines),
            "住宅图片": self.parse_house_images(lines)
        }
        
        return result
    
    def save_json(self, result: Dict[str, Any], output_path: str):
        """Save parsed result to JSON file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

def run(project_name: str, file_path: str = "resources/working_data/test_log_housing.txt") -> Dict[str, Any]:
    """Run the parser with a given project name and file path."""
    parser = CRICHousingParser()
    
    # Parse the housing data
    result = parser.parse_all_sections(file_path)
    
    # Define timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    
    # Create output directory
    output_dir = Path(f"resources/working_data/{project_name}_{timestamp}/processed_data")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    output_path = output_dir / f"{project_name}_房子基本信息.json"
    parser.save_json(result, output_path)
    
    print(f"Parsing completed! Results saved to {output_path}")
    
    return result

if __name__ == "__main__":
    # For testing purposes, use a default project name
    result = run(project_name="华发四季半岛")
    print("\n企业信息 section:")
    print(json.dumps(result["企业信息"], ensure_ascii=False, indent=2))