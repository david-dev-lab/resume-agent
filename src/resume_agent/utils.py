import os
from jinja2 import Environment, FileSystemLoader

def save_as_html(data: dict, output_path: str):
    # 1. 确定模板目录和文件名
    current_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(current_dir, "templates")
    
    # 2. 设置 Jinja2 环境
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("resume_v1.html")
    
    # 3. 渲染
    html_content = template.render(**data)
    
    # 4. 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"✨ 简历已渲染完成: {os.path.abspath(output_path)}")
