import os
import math
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

def render_html(data: dict) -> str:
    """仅渲染 HTML 内容，不保存文件"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, "templates")
    
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("resume_v1.html")
    
    return template.render(**data)

def save_as_html(data: dict, output_path: str):
    """保存为 HTML 文件"""
    html_content = render_html(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✨ HTML 简历已生成: {os.path.abspath(output_path)}")

def save_as_pdf(html_path: str, output_path: str):
    """
    保存为 PDF 文件 (使用 Playwright 浏览器渲染)
    强制将内容缩放至一页 (One Page Policy)
    """
    abs_html_path = os.path.abspath(html_path)
    if not os.path.exists(abs_html_path):
        raise FileNotFoundError(f"HTML 文件未找到: {abs_html_path}")

    print(f"📄 正在调用 Playwright 渲染 PDF (源文件: {abs_html_path})...")
    
    with sync_playwright() as p:
        # 启动无头浏览器
        browser = p.chromium.launch()
        page = browser.new_page()
        
        # 打开本地 HTML 文件
        page.goto(f"file://{abs_html_path}")
        page.wait_for_load_state("networkidle")

        # --- 智能缩放算法 (Smart Scaling) ---
        # A4 纸张在 96 DPI 下的高度约为 1123px。减去上下安全边距，可用高度约 1080px。
        MAX_HEIGHT = 1080 
        
        # 获取实际内容高度
        content_height = page.evaluate("document.body.scrollHeight")
        print(f"📏 简历原始内容高度: {content_height}px")

        scale_factor = 1.0
        if content_height > MAX_HEIGHT:
            # 计算需要的缩放比例
            scale_factor = MAX_HEIGHT / content_height
            # 为了美观，设置最小缩放底线 0.75 (再小就看不清了)
            scale_factor = max(scale_factor, 0.75) 
            
            print(f"📐 检测到内容溢出，正在执行智能缩放: {scale_factor:.2f}x")
            
            # 使用 CSS zoom 进行缩放 (Chrome 内核支持良好)
            page.evaluate(f"document.body.style.zoom = '{scale_factor}'")

        # 生成 PDF (A4 格式，保留背景色)
        page.pdf(
            path=output_path,
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            # 注意：playwright 的 scale 参数是页面级别的，我们已经用 CSS zoom 处理了内容，所以这里保持 1.0
            scale=1.0 
        )
        
        browser.close()
    
    print(f"✅ PDF 简历已完美生成 (One Page Mode): {os.path.abspath(output_path)}")
