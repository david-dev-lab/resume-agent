import os
import argparse
from dotenv import load_dotenv
from .core import ResumeAgent
from .utils import save_as_html, save_as_pdf

def load_text(file_path: str) -> str:
    if not os.path.exists(file_path):
        print(f"⚠️  警告: 文件未找到 - {file_path}")
        return ""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    parser = argparse.ArgumentParser(description="Resume Agent - 极速简历生成器")
    parser.add_argument("--thoughts", default="data/raw_thoughts.md", help="包含原始经历/思绪的 Markdown 文件路径")
    parser.add_argument("--jd", default="data/target_jd.txt", help="包含目标职位描述 (JD) 的文本文件路径")
    parser.add_argument("--output", default="output/tailored_resume.html", help="生成的 HTML 简历保存路径")
    parser.add_argument("--model", default="deepseek-chat", help="使用的 LLM 模型 (默认: deepseek-chat)")
    
    args = parser.parse_args()

    load_dotenv()
    
    # 实例化
    print(f"🤖 初始化 Agent (Model: {args.model})...")
    agent = ResumeAgent(model=args.model)
    
    print(f"📂 读取输入文件:\n  - Thoughts: {args.thoughts}\n  - JD: {args.jd}")
    thoughts = load_text(args.thoughts)
    jd = load_text(args.jd)
    
    if not thoughts or not jd:
        print("❌ 错误: 输入内容为空，请检查文件路径。")
        return

    print("🚀 正在将乱麻思绪转化为精美简历 (这可能需要 30-60 秒)...")
    try:
        result = agent.tailor(thoughts, jd)
        
        # 1. 保存为 HTML
        save_as_html(result.model_dump(), args.output)
        
        # 2. 默认同时生成 PDF (使用 Playwright)
        pdf_path = args.output.replace(".html", ".pdf")
        try:
            # 注意：这里我们直接传递 HTML 文件路径，而不是数据
            # 这样 Playwright 就能渲染出和浏览器一模一样的效果
            save_as_pdf(args.output, pdf_path)
        except Exception as e:
            print(f"⚠️ PDF 生成出错: {e}")
            if "playwright" in str(e).lower() or "browser" in str(e).lower():
                print("💡 提示: 似乎是 Playwright 环境问题。请尝试运行: playwright install")

        # 尝试自动打开 HTML (兼容 Mac/Linux)
        # 优先打开 PDF (如果生成成功)，否则打开 HTML
        try:
            target_to_open = pdf_path if os.path.exists(pdf_path) else args.output
            if os.name == 'posix':
                os.system(f"open '{target_to_open}'")
            elif os.name == 'nt':
                os.startfile(target_to_open)
        except Exception:
            pass
            
    except Exception as e:
        print(f"❌ 程序异常终止: {str(e)}")

if __name__ == "__main__":
    main()
