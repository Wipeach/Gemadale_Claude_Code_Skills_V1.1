# 图片视觉校验规则（zai-mcp-server）

对每张候选图片输出：
- match: true/false
- reason: 为什么匹配/不匹配（是否与页面主题、供应商、品类、型号一致）
- tags: ["logo","product","case","certificate","factory","other"]
- quality: "high|medium|low"（清晰度/水印/可读性）

过滤规则：
- match=false 必须剔除
- quality=low 且无替代时可降级使用，但需优先补图替换
