# PPTX Plan 输出格式（结构化）

请输出 JSON：
{
  "meta": {"title":"", "audience":"", "tone":"", "page_count":10},
  "template": {"use_input_template": true/false, "path": ""},
  "slides":[
    {
      "index": 1,
      "title": "",
      "pattern": "Cover-HeroImage",
      "bullets": ["", ""],
      "data_needs": [{"type":"stat|table|quote", "topic":"", "source_hint":""}],
      "image_needs": [{"type":"logo|product|case|chart|hero", "keywords":["",""], "must_match":true}],
      "chart_suggestion": "bar|line|matrix|timeline|none",
      "sources": []
    }
  ]
}
