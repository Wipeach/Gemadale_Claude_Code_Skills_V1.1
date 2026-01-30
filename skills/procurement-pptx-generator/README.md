# procurement-pptx-generator

金地上海采购部：基于 PPTX 模板（可选）+ 提示词文件（必选），自动生成高质感、多版式、含联网证据与图片校验的 PPTX。

## 输入
- ppt_template（可选）：PPTX模板
- prompt_file（必选）：提示词文件（txt/md）

## 行为
- 无模板则使用 templates/default_template.pptx
- 使用 MCP：web-search-prime + web-reader + zai-mcp-server 生成内容与筛选图片
- 图片数量 >= 页数 × 60%
- 版式多样：至少 70% 页面布局不同

## 输出
- output.pptx
