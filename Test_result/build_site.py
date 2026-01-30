# -*- coding: utf-8 -*-
"""
金地集团投资部｜投资分析报告网站生成器
根据 full.md + images/ 生成完整的投资分析报告网站
"""
import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any

# Configuration
SOURCE_DIR = Path(r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result\extracted_content')
OUTPUT_DIR = Path(r'D:\VSCode\A_AI_Project\Anthropics_skills_git\gemdale-sh-cc-skills-main\Test_result\website')
FULL_MD_PATH = SOURCE_DIR / 'full.md'
IMAGES_DIR = SOURCE_DIR / 'images'

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / 'assets').mkdir(exist_ok=True)
(OUTPUT_DIR / 'assets' / 'images').mkdir(exist_ok=True)

# Copy images to output
print("Copying images...")
for img in IMAGES_DIR.glob('*'):
    shutil.copy(img, OUTPUT_DIR / 'assets' / 'images' / img.name)

print(f"Found {len(list(IMAGES_DIR.glob('*')))} images")

# Parse full.md
print("Parsing full.md...")
with open(FULL_MD_PATH, 'r', encoding='utf-8') as f:
    md_content = f.read()

# Split by pages
pages = re.split(r'## Page \d+', md_content)[1:]  # Skip first empty part

print(f"Found {len(pages)} pages")

# Build report data structure
report_data = {
    "meta": {
        "title": "松江区泗泾04-08号地块投资分析报告",
        "subtitle": "金地集团投资部",
        "date": "2026年"
    },
    "parts": []
}

# Find part boundaries
current_part = None
current_section = None
page_content = []

# Parse pages into parts
for i, page in enumerate(pages, 1):
    page_num = i
    content = page.strip()

    # Detect part headers
    part_match = re.search(r'(PART\d+)(.+)', content)
    if part_match:
        if current_part:
            report_data["parts"].append(current_part)
        part_id = part_match.group(1).lower()
        part_title = part_match.group(2).strip()
        current_part = {
            "part_id": part_id,
            "title": part_title,
            "sections": [],
            "page_range": [page_num, page_num]
        }

    # Detect sections
    section_match = re.search(r'^(\d+\.\d+)\s+(.+)$', content, re.MULTILINE)
    if section_match and current_part:
        section_id = section_match.group(1)
        section_title = section_match.group(2).strip()
        current_section = {
            "id": section_id.replace('.', ''),
            "title": section_title,
            "content": content,
            "page_num": page_num,
            "blocks": []
        }
        if current_part:
            current_part["sections"].append(current_section)
    elif current_part and not current_section:
        # First section without explicit header
        current_section = {
            "id": f"{current_part['part_id']}_intro",
            "title": "概述",
            "content": content,
            "page_num": page_num,
            "blocks": []
        }
        current_part["sections"].append(current_section)

    if current_part:
        current_part["page_range"][1] = page_num

# Add last part
if current_part:
    report_data["parts"].append(current_part)

print(f"Found {len(report_data['parts'])} parts")
for part in report_data['parts']:
    print(f"  {part['part_id']}: {part['title']} - {len(part['sections'])} sections")

# Extract images mapping
page_images = {}
for img in IMAGES_DIR.glob('*'):
    match = re.search(r'page(\d+)_img\d+\.(png|jpg|jpeg)', img.name)
    if match:
        page_num = int(match.group(1))
        if page_num not in page_images:
            page_images[page_num] = []
        page_images[page_num].append(img.name)

print(f"\nImage mapping: {len(page_images)} pages have images")

# Generate report_data.json
with open(OUTPUT_DIR / 'assets' / 'report_data.json', 'w', encoding='utf-8') as f:
    json.dump(report_data, f, ensure_ascii=False, indent=2)

# Now generate the website
print("\nGenerating website...")

# Design Tokens (CSS Variables)
THEME_CSS = """/* Design Tokens - 金地集团投资部 */
:root {
  /* Colors */
  --color-bg: #FFFFFF;
  --color-surface: #FAFAFA;
  --color-surface-elevated: #F5F5F5;
  --color-text: #1A1A1A;
  --color-text-secondary: #666666;
  --color-text-muted: #999999;
  --color-border: #E0E0E0;
  --color-border-light: #F0F0F0;
  --color-accent: #FF6B00;
  --color-accent-hover: #E55F00;
  --color-accent-weak: #FFF0E6;
  --color-accent-text: #FFFFFF;
  --color-success: #52C41A;
  --color-warning: #FAAD14;
  --color-error: #F5222D;

  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  --spacing-3xl: 64px;

  /* Typography */
  --font-family-base: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-2xl: 24px;
  --font-size-3xl: 30px;
  --font-size-4xl: 36px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-semibold: 600;
  --font-weight-bold: 700;
  --line-height-tight: 1.25;
  --line-height-normal: 1.5;
  --line-height-relaxed: 1.75;

  /* Borders */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --border-width: 1px;
  --border-width-thick: 2px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.07);
  --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px rgba(0, 0, 0, 0.15);

  /* Layout */
  --header-height: 64px;
  --sidebar-width: 280px;
  --content-max-width: 1400px;
  --container-max-width: 1200px;
}
"""

# Main Styles
STYLES_CSS = """/* Main Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-md);
  line-height: var(--line-height-normal);
  color: var(--color-text);
  background-color: var(--color-bg);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
  font-weight: var(--font-weight-semibold);
  line-height: var(--line-height-tight);
  margin-bottom: var(--spacing-md);
}

h1 { font-size: var(--font-size-4xl); }
h2 { font-size: var(--font-size-3xl); }
h3 { font-size: var(--font-size-2xl); }
h4 { font-size: var(--font-size-xl); }
h5 { font-size: var(--font-size-lg); }
h6 { font-size: var(--font-size-md); }

p {
  margin-bottom: var(--spacing-md);
}

a {
  color: var(--color-accent);
  text-decoration: none;
  transition: color 0.2s;
}

a:hover {
  color: var(--color-accent-hover);
}

/* Header */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--header-height);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: var(--border-width) solid var(--color-border);
  z-index: 1000;
  display: flex;
  align-items: center;
  padding: 0 var(--spacing-xl);
}

.header-content {
  max-width: var(--content-max-width);
  width: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text);
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: var(--color-accent);
  color: white;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-weight-bold);
}

/* Top Navigation */
.top-nav {
  display: flex;
  gap: var(--spacing-xs);
}

.top-nav a {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  transition: all 0.2s;
}

.top-nav a:hover,
.top-nav a.active {
  color: var(--color-accent);
  background: var(--color-accent-weak);
}

/* Layout */
.main-container {
  display: flex;
  margin-top: var(--header-height);
  min-height: calc(100vh - var(--header-height));
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-surface);
  border-right: var(--border-width) solid var(--color-border);
  position: fixed;
  left: 0;
  top: var(--header-height);
  bottom: 0;
  overflow-y: auto;
  padding: var(--spacing-lg);
  z-index: 100;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.sidebar-nav a {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  transition: all 0.2s;
  display: block;
}

.sidebar-nav a:hover,
.sidebar-nav a.active {
  color: var(--color-accent);
  background: var(--color-accent-weak);
  font-weight: var(--font-weight-medium);
}

.sidebar-nav .section-header {
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: var(--spacing-lg);
  margin-bottom: var(--spacing-sm);
  padding-left: var(--spacing-md);
}

/* Content */
.content {
  margin-left: var(--sidebar-width);
  flex: 1;
  padding: var(--spacing-2xl);
  max-width: calc(100% - var(--sidebar-width));
}

.content-inner {
  max-width: var(--container-max-width);
  margin: 0 auto;
}

/* Sections */
.section {
  margin-bottom: var(--spacing-3xl);
  scroll-margin-top: calc(var(--header-height) + var(--spacing-lg));
}

.section-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: var(--border-width-thick) solid var(--color-accent);
}

/* Cards */
.card {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
}

.card-title {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  margin-bottom: var(--spacing-md);
}

/* Grid Layouts */
.grid-2 {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-lg);
}

.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--spacing-lg);
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-md);
}

.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin: var(--spacing-lg) 0;
}

.image-item {
  position: relative;
  overflow: hidden;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: transform 0.2s;
}

.image-item:hover {
  transform: scale(1.05);
}

.image-item img {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

/* Tables */
table {
  width: 100%;
  border-collapse: collapse;
  margin: var(--spacing-lg) 0;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

thead {
  background: var(--color-accent);
  color: var(--color-accent-text);
}

th, td {
  padding: var(--spacing-md);
  text-align: left;
  border-bottom: var(--border-width) solid var(--color-border);
}

th {
  font-weight: var(--font-weight-semibold);
}

tbody tr:hover {
  background: var(--color-surface-elevated);
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-lg) 0;
}

.kpi-card {
  background: linear-gradient(135deg, var(--color-accent) 0%, var(--color-accent-hover) 100%);
  color: white;
  padding: var(--spacing-lg);
  border-radius: var(--radius-lg);
  text-align: center;
}

.kpi-value {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-xs);
}

.kpi-label {
  font-size: var(--font-size-sm);
  opacity: 0.9;
}

/* Key Takeaways */
.takeaways {
  background: var(--color-accent-weak);
  border-left: 4px solid var(--color-accent);
  padding: var(--spacing-lg);
  border-radius: var(--radius-md);
  margin: var(--spacing-lg) 0;
}

.takeaways ul {
  list-style: none;
}

.takeaways li {
  padding: var(--spacing-sm) 0;
  padding-left: var(--spacing-lg);
  position: relative;
}

.takeaways li:before {
  content: "▪";
  position: absolute;
  left: 0;
  color: var(--color-accent);
  font-size: var(--font-size-xl);
}

/* Tabs */
.tabs {
  display: flex;
  gap: var(--spacing-xs);
  border-bottom: var(--border-width) solid var(--color-border);
  margin-bottom: var(--spacing-lg);
}

.tab {
  padding: var(--spacing-sm) var(--spacing-lg);
  border: none;
  background: none;
  cursor: pointer;
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab:hover {
  color: var(--color-accent);
}

.tab.active {
  color: var(--color-accent);
  border-bottom-color: var(--color-accent);
}

.tab-content {
  display: none;
}

.tab-content.active {
  display: block;
}

/* Part4 Design Options */
.design-option {
  margin-bottom: var(--spacing-3xl);
}

.design-option-header {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-lg);
}

.design-option-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
}

.design-option-badge {
  background: var(--color-accent);
  color: white;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
}

.design-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
}

.design-main-image {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.design-main-image img {
  width: 100%;
  height: 400px;
  object-fit: cover;
}

.design-specs {
  background: var(--color-surface);
  border: var(--border-width) solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
}

.advantages-list {
  margin-top: var(--spacing-lg);
}

.advantages-list li {
  padding: var(--spacing-sm) 0;
  border-bottom: var(--border-width) solid var(--color-border-light);
}

.advantages-list li:last-child {
  border-bottom: none;
}

/* Lightbox */
.lightbox {
  display: none;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  z-index: 9999;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.lightbox.active {
  display: flex;
}

.lightbox img {
  max-width: 90%;
  max-height: 90%;
  object-fit: contain;
}

.lightbox-close {
  position: absolute;
  top: var(--spacing-lg);
  right: var(--spacing-lg);
  background: white;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  font-size: var(--font-size-xl);
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Footer */
.footer {
  background: var(--color-surface);
  border-top: var(--border-width) solid var(--color-border);
  padding: var(--spacing-2xl) 0;
  margin-top: var(--spacing-3xl);
  text-align: center;
  color: var(--color-text-muted);
}

/* Mobile Menu */
.mobile-menu-btn {
  display: none;
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  padding: var(--spacing-sm);
}

@media (max-width: 768px) {
  .top-nav {
    display: none;
  }

  .mobile-menu-btn {
    display: block;
  }

  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.3s;
  }

  .sidebar.active {
    transform: translateX(0);
  }

  .content {
    margin-left: 0;
    padding: var(--spacing-lg);
    max-width: 100%;
  }

  .grid-2,
  .grid-3,
  .grid-4 {
    grid-template-columns: 1fr;
  }

  .design-grid {
    grid-template-columns: 1fr;
  }
}

/* Print Styles */
@media print {
  .header,
  .sidebar,
  .footer {
    display: none;
  }

  .content {
    margin-left: 0;
    padding: 0;
  }

  .section {
    page-break-inside: avoid;
  }

  a {
    color: var(--color-text);
  }
}
"""

# JavaScript for interactivity
APP_JS = """// Website Interactivity
document.addEventListener('DOMContentLoaded', function() {

  // Scrollspy for navigation
  const sections = document.querySelectorAll('.section[id]');
  const topNavLinks = document.querySelectorAll('.top-nav a');
  const sidebarLinks = document.querySelectorAll('.sidebar-nav a');

  function updateActiveNav() {
    let currentSection = '';
    const scrollPos = window.scrollY + 100;

    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        currentSection = section.getAttribute('id');
      }
    });

    topNavLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + currentSection) {
        link.classList.add('active');
      }
    });

    sidebarLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === '#' + currentSection) {
        link.classList.add('active');
      }
    });
  }

  window.addEventListener('scroll', updateActiveNav);
  updateActiveNav();

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Lightbox for images
  const lightbox = document.querySelector('.lightbox');
  const lightboxImg = lightbox?.querySelector('img');
  const lightboxClose = lightbox?.querySelector('.lightbox-close');

  document.querySelectorAll('.image-item img').forEach(img => {
    img.addEventListener('click', function() {
      if (lightbox && lightboxImg) {
        lightboxImg.src = this.src.replace('150', '800');
        lightbox.classList.add('active');
      }
    });
  });

  if (lightboxClose) {
    lightboxClose.addEventListener('click', () => {
      lightbox.classList.remove('active');
    });
  }

  if (lightbox) {
    lightbox.addEventListener('click', (e) => {
      if (e.target === lightbox) {
        lightbox.classList.remove('active');
      }
    });
  }

  // Tabs functionality
  document.querySelectorAll('.tabs').forEach(tabContainer => {
    const tabs = tabContainer.querySelectorAll('.tab');
    const contents = tabContainer.parentElement?.querySelectorAll('.tab-content') || [];

    tabs.forEach(tab => {
      tab.addEventListener('click', function() {
        tabs.forEach(t => t.classList.remove('active'));
        this.classList.add('active');

        const targetId = this.getAttribute('data-tab');
        contents.forEach(content => {
          content.classList.remove('active');
          if (content.id === targetId) {
            content.classList.add('active');
          }
        });
      });
    });
  });

  // Mobile menu toggle
  const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');

  if (mobileMenuBtn && sidebar) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking a link
    sidebar.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        sidebar.classList.remove('active');
      });
    });
  }

  // Lazy load images
  const images = document.querySelectorAll('img[data-src]');
  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.removeAttribute('data-src');
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach(img => imageObserver.observe(img));
});
"""

# Generate CSS files
with open(OUTPUT_DIR / 'assets' / 'theme.css', 'w', encoding='utf-8') as f:
    f.write(THEME_CSS)

with open(OUTPUT_DIR / 'assets' / 'styles.css', 'w', encoding='utf-8') as f:
    f.write(STYLES_CSS)

with open(OUTPUT_DIR / 'assets' / 'print.css', 'w', encoding='utf-8') as f:
    f.write("")  # Add print-specific styles if needed

with open(OUTPUT_DIR / 'assets' / 'app.js', 'w', encoding='utf-8') as f:
    f.write(APP_JS)

print("Generated CSS and JS files")

# Now generate the main HTML
print("Generating HTML...")

# Generate sections HTML based on parsed data
def generate_part_html(part):
    html = f'<section id="{part["part_id"]}" class="section">\n'
    html += f'  <h2 class="section-title">{part["title"]}</h2>\n'

    for section in part.get("sections", []):
        html += f'  <div class="card">\n'
        html += f'    <h3 class="card-title">{section.get("title", "")}</h3>\n'

        # Add images if available
        page_num = section.get("page_num", 0)
        if page_num in page_images:
            html += f'    <div class="image-gallery">\n'
            for img in page_images[page_num][:4]:  # Limit to 4 images
                html += f'      <div class="image-item">\n'
                html += f'        <img src="assets/images/{img}" alt="{section.get("title", "")}" loading="lazy">\n'
                html += f'      </div>\n'
            html += f'    </div>\n'

        html += f'    <div class="content-text">\n'
        # Extract and format text content
        content = section.get("content", "")
        # Clean up content - remove page numbers and markers
        content = re.sub(r'^\d+$', '', content, flags=re.MULTILINE)
        content = re.sub(r'◼', '', content)
        content = re.sub(r'✓', '', content)
        lines = content.split('\n')
        for line in lines[:20]:  # Limit lines
            line = line.strip()
            if line and len(line) > 3:
                html += f'      <p>{line}</p>\n'
        html += f'    </div>\n'
        html += f'  </div>\n'

    html += f'</section>\n'
    return html

# Build complete HTML
html_parts = []

# HTML Header
html_parts.append("""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>松江区泗泾04-08号地块投资分析报告 | 金地集团投资部</title>
  <link rel="stylesheet" href="assets/theme.css">
  <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="header-content">
      <div class="logo">
        <div class="logo-icon">金</div>
        <span>金地集团投资部</span>
      </div>
      <nav class="top-nav">
        <a href="#home" class="active">首页</a>
        <a href="#part1">项目概况</a>
        <a href="#part2">市场竞争</a>
        <a href="#part3">客户定位</a>
        <a href="#part4">设计方案</a>
        <a href="#part5">运营计划</a>
        <a href="#part6">投资测算</a>
      </nav>
      <button class="mobile-menu-btn">☰</button>
    </div>
  </header>

  <!-- Main Container -->
  <div class="main-container">
    <!-- Sidebar -->
    <aside class="sidebar">
      <nav class="sidebar-nav">
        <a href="#home">首页</a>
""")

# Add sidebar links for each part
for part in report_data["parts"]:
    part_id = part["part_id"]
    part_title = part["title"]
    html_parts.append(f'        <span class="section-header">{part_title}</span>')
    for section in part.get("sections", [])[:5]:  # Limit sections
        section_title = section.get("title", "")[:15]  # Truncate long titles
        section_id = section.get("id", "")
        html_parts.append(f'        <a href="#{section_id}">{section_title}</a>')

html_parts.append("""      </nav>
    </aside>

    <!-- Content -->
    <main class="content">
      <div class="content-inner">
""")

# Add home/hero section
html_parts.append("""        <!-- Hero Section -->
        <section id="home" class="section">
          <div style="text-align: center; padding: 60px 20px;">
            <h1 style="font-size: 48px; margin-bottom: 20px;">松江区泗泾04-08号地块</h1>
            <h2 style="font-size: 32px; color: var(--color-accent); margin-bottom: 40px;">投资分析报告</h2>
            <p style="font-size: 18px; color: var(--color-text-secondary);">金地集团投资部 | 2026年</p>
          </div>

          <div class="kpi-grid">
            <div class="kpi-card">
              <div class="kpi-value">1.93万㎡</div>
              <div class="kpi-label">占地面积</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-value">1.2</div>
              <div class="kpi-label">容积率</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-value">2.32万㎡</div>
              <div class="kpi-label">计容建面</div>
            </div>
            <div class="kpi-card">
              <div class="kpi-value">2.3万/㎡</div>
              <div class="kpi-label">起拍楼板价</div>
            </div>
          </div>
        </section>
""")

# Add all parts
for part in report_data["parts"]:
    html_parts.append(generate_part_html(part))

# HTML Footer
html_parts.append("""
      </div>
    </main>
  </div>

  <!-- Lightbox -->
  <div class="lightbox" id="lightbox">
    <button class="lightbox-close">×</button>
    <img src="" alt="放大图片">
  </div>

  <!-- Footer -->
  <footer class="footer">
    <p>© 2026 金地集团投资部 | 内部资料，请勿外传</p>
  </footer>

  <script src="assets/app.js"></script>
</body>
</html>
""")

# Write complete HTML
with open(OUTPUT_DIR / 'index.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(html_parts))

print(f"\n✅ Website generated successfully!")
print(f"📁 Output directory: {OUTPUT_DIR}")
print(f"🌐 Open {OUTPUT_DIR / 'index.html'} in your browser")
