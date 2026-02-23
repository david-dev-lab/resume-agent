import os
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML, CSS

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

def save_as_pdf(data: dict, output_path: str):
    """保存为 PDF 文件 (使用 WeasyPrint)"""
    html_content = render_html(data)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 定义 PDF 专用的 CSS，确保 A4 纸张布局完美
    pdf_css = CSS(string='''
        @page {
            size: A4;
            margin: 0;
        }
        body {
            font-family: "PingFang SC", "Microsoft YaHei", sans-serif; /* 确保中文显示正常 */
        }
    ''')

    # 使用 WeasyPrint 将 HTML 字符串直接转为 PDF
    HTML(string=html_content).write_pdf(output_path, stylesheets=[pdf_css])
    
    print(f"📄 PDF 简历已生成: {os.path.abspath(output_path)}")
