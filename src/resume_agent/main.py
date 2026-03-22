import os
import argparse
from dotenv import load_dotenv
from .core import ResumeAgent
from .utils import load_text, save_as_html, save_as_pdf


def main():
    parser = argparse.ArgumentParser(description="Resume Agent - 极速简历生成器")
    parser.add_argument("--thoughts", default="data/raw_thoughts.md", help="包含原始经历/思绪的 Markdown 文件路径")
    parser.add_argument("--jd", default="data/target_jd.txt", help="包含目标职位描述 (JD) 的文本文件路径")
    parser.add_argument("--output", default="output/tailored_resume.html", help="生成的 HTML 简历保存路径")
    parser.add_argument("--model", default="deepseek-chat", help="使用的 LLM 模型 (默认: deepseek-chat)")
    parser.add_argument("--template", default="swiss_single_column.html", help="使用的 HTML 模板名称 (例如: modern_two_column.html)")
    
    args = parser.parse_args()
    load_dotenv()
    
    print(f"🚀 Resume Agent 启动 (Model: {args.model} | Template: {args.template})")
    
    try:
        raw_thoughts = load_text(args.thoughts)
        jd_text = load_text(args.jd)
    except FileNotFoundError as e:
        print(f"❌ {e}")
        return

    agent = ResumeAgent(model=args.model)
    try:
        result = agent.build_resume(raw_thoughts, jd_text, template_name=args.template)
        
        # 打印最终匹配分
        print(f"🎯 最终简历 JD 匹配分: {result.match_score}/100")

        # 1. 保存 HTML (静默)
        save_as_html(result.model_dump(), args.output, template_name=args.template)
        
        # 2. 生成 PDF
        pdf_path = args.output.replace(".html", ".pdf")
        try:
            save_as_pdf(args.output, pdf_path)
        except Exception as e:
            print(f"⚠️ PDF 生成出错: {e}")
            if "playwright" in str(e).lower():
                print("💡 请尝试运行: playwright install")

        import webbrowser
        try:
            target = pdf_path if os.path.exists(pdf_path) else args.output
            webbrowser.open(f"file://{os.path.abspath(target)}")
        except Exception:
            pass
            
    except Exception as e:
        print(f"❌ 运行中断: {str(e)}")

if __name__ == "__main__":
    main()
