import os
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright


def load_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_text(content: str, file_path: str) -> None:
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)


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

        A4_HEIGHT_PX = 1123  # A4 @ 96dpi
        content_height = page.evaluate("document.body.scrollHeight")
        scale = min(A4_HEIGHT_PX / content_height, 1.0) if content_height > A4_HEIGHT_PX else 1.0
        scale = max(scale, 0.75)

        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            scale=scale,
        )
        browser.close()
    
    # 只输出最终的成功文件路径，使用相对路径更友好
    rel_path = os.path.relpath(output_path)
    print(f"🎉 简历生成成功！\n👉 {rel_path}")
