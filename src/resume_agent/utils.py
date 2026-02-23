import os
import math
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

def render_html(data: dict) -> str:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, "templates")
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("resume_v1.html")
    return template.render(**data)

def save_as_html(data: dict, output_path: str):
    html_content = render_html(data)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    # 保持安静，不输出日志

def save_as_pdf(html_path: str, output_path: str):
    abs_html_path = os.path.abspath(html_path)
    if not os.path.exists(abs_html_path):
        raise FileNotFoundError(f"HTML 文件未找到: {abs_html_path}")

    # 简化输出
    print("📄 正在生成 PDF (智能排版中)...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{abs_html_path}")
        page.wait_for_load_state("networkidle")

        # Smart Scaling
        MAX_HEIGHT = 1080 
        content_height = page.evaluate("document.body.scrollHeight")
        
        if content_height > MAX_HEIGHT:
            scale_factor = max(MAX_HEIGHT / content_height, 0.75)
            page.evaluate(f"document.body.style.zoom = '{scale_factor}'")

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            scale=1.0 
        )
        browser.close()
    
    # 只输出最终的成功文件路径，使用相对路径更友好
    rel_path = os.path.relpath(output_path)
    print(f"🎉 简历生成成功！\n👉 {rel_path}")
