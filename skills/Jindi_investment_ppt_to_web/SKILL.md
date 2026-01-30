---
name: Jindi_investment_ppt_to_wweb
description: |
"金地集团【投资部】专项 Skill：实现功能为将投资部的PPT或者PDF转为成为投资部网站。Convert PowerPoint presentations to professional investment analysis websites. Orchestrates the complete workflow: converts PPTX to PDF, extracts content using MinerU, and builds a Jindi Investment branded website. Use when converting investment presentations, pitch decks, or financial reports to web format, or when the user mentions converting PPT/PPTX files to websites."

---


# Jindi Investment PPT to Web Converter

## Overview

This skill orchestrates a three-stage workflow to convert PowerPoint presentations into professional investment analysis websites with Jindi Investment branding.

## Quick Reference

| Stage | Skill Used | Purpose |
|-------|-----------|---------|
| 1. Convert | pptx-to-pdf | Convert PPTX to PDF format |
| 2. Extract | minerU | Extract text, tables, images from PDF |
| 3. Build | jindi_investment_build_site | Generate branded investment website |

## Complete Workflow

Follow these steps in order. Complete each stage before proceeding to the next.

### Stage 1: PPTX to PDF Conversion

**Skill to invoke**: `pptx-to-pdf`

Convert the PowerPoint presentation to PDF format:

```bash
# The pptx-to-pdf skill will handle this conversion
# Input: presentation.pptx
# Output: presentation.pdf
```

**What to do**:
1. Invoke the `pptx-to-pdf` skill
2. Provide the input PPTX file path
3. Verify the PDF output is created successfully
4. Note the output PDF file path for the next stage

**Before proceeding**: Confirm the PDF file exists and is readable.

---

### Stage 2: Content Extraction with MinerU

**Skill to invoke**: `minerU`

Extract content from the PDF using MinerU:

```bash
# The minerU skill will extract:
# - Text content
# - Tables and data
# - Images and charts
# Input: presentation.pdf
# Output: Structured content (markdown, JSON, or similar format)
```

**What to do**:
1. Invoke the `minerU` skill
2. Provide the PDF file path from Stage 1
3. MinerU will extract all content into structured format
4. Review the extracted content to ensure completeness
5. Note the extraction output location

**Expected outputs**:
- Text content in markdown or structured format
- Extracted tables (if any)
- Extracted images/charts (if any)
- Metadata about the presentation

**Before proceeding**: Verify all critical content has been extracted successfully.

---

### Stage 3: Build Investment Website

**Skill to invoke**: `jindi_investment_build_site`

Generate the Jindi Investment branded website:

```bash
# The jindi_investment_build_site skill will:
# - Apply Jindi Investment branding
# - Structure content for investment analysis
# - Create navigation and layout
# - Generate final HTML/CSS/JS website
# Input: Extracted content from Stage 2
# Output: Complete website directory
```

**What to do**:
1. Invoke the `jindi_investment_build_site` skill
2. Provide the extracted content from Stage 2
3. The skill will build a complete website with:
   - Jindi Investment branding
   - Professional investment analysis layout
   - Interactive charts and tables
   - Responsive design
4. Verify the website is generated correctly
5. Provide the website output location to the user

**Final output**: A complete, ready-to-deploy website in the output directory.

---

## Workflow Checklist

Copy this checklist and check off items as you complete them:

```
PPT to Web Conversion Progress:
- [ ] Stage 1: Convert PPTX to PDF (pptx-to-pdf skill)
- [ ] Stage 1 Verification: PDF file created successfully
- [ ] Stage 2: Extract content with MinerU (minerU skill)
- [ ] Stage 2 Verification: Content extracted completely
- [ ] Stage 3: Build website (jindi_investment_build_site skill)
- [ ] Stage 3 Verification: Website generated successfully
- [ ] Final: Deliver website to user
```

## Error Handling

If any stage fails:

1. **Stage 1 fails (PPTX to PDF)**:
   - Check that the input file is a valid PPTX
   - Verify file permissions
   - Check if pptx-to-pdf skill is available
   - Retry or report error to user

2. **Stage 2 fails (Content Extraction)**:
   - Verify the PDF from Stage 1 is valid
   - Check if minerU skill is available
   - Some complex layouts may not extract perfectly - inform user
   - Retry or proceed with partial extraction if acceptable

3. **Stage 3 fails (Website Building)**:
   - Verify extracted content from Stage 2 is complete
   - Check if jindi_investment_build_site skill is available
   - Review error messages for missing required content
   - Retry after fixing issues

## Skill Dependencies

This skill requires the following skills to be available:

1. **pptx-to-pdf**: For PowerPoint to PDF conversion
   - Location: `/mnt/skills/user/pptx-to-pdf/SKILL.md` (or similar)
   - Purpose: Stage 1 conversion

2. **minerU**: For content extraction from PDF
   - Location: `/mnt/skills/user/minerU/SKILL.md` (or similar)
   - Purpose: Stage 2 extraction

3. **jindi_investment_build_site**: For website generation
   - Location: `/mnt/skills/user/jindi_investment_build_site/SKILL.md` (or similar)
   - Purpose: Stage 3 website building

**Important**: All three skills must be available for this workflow to complete successfully.

## Usage Example

**User request**: "Convert my investment pitch deck presentation.pptx into a website"

**Workflow**:
1. Invoke `pptx-to-pdf` skill → Creates `presentation.pdf`
2. Invoke `minerU` skill with `presentation.pdf` → Extracts content
3. Invoke `jindi_investment_build_site` skill with extracted content → Generates website
4. Deliver completed website to user

## Best Practices

1. **Sequential execution**: Always complete stages in order (1→2→3)
2. **Verify each stage**: Check outputs before proceeding to next stage
3. **Error early**: Stop and report if any stage fails critically
4. **Inform user**: Keep user updated on progress through each stage
5. **File management**: Keep intermediate files organized and named clearly

## Limitations

- Requires all three dependent skills to be available
- Complex PowerPoint animations may not transfer to web format
- Some advanced formatting may be lost during PDF conversion
- Content extraction quality depends on PDF structure
- Final website styling is determined by jindi_investment_build_site skill

## Notes

This is an orchestration skill that does not execute code directly. Instead, it coordinates the execution of three specialized skills in sequence to achieve the complete PPT-to-web conversion workflow.