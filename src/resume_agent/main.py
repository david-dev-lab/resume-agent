import os
import argparse
from dotenv import load_dotenv
from .core import ResumeAgent
from .utils import save_as_html, save_as_pdf

def load_text(file_path: str) -> str:
    if not os.path.exists(file_path):
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
    
    # 简单的启动提示
    print(f"🚀 Resume Agent 启动 (Model: {args.model})")
    
    agent = ResumeAgent(model=args.model)
    thoughts = load_text(args.thoughts)
    jd = load_text(args.jd)
    
    if not thoughts or not jd:
        print("❌ 错误: 输入内容为空，请检查文件路径。")
        return

    try:
        result = agent.tailor(thoughts, jd)
        
        # 打印最终匹配分
        print(f"🎯 最终简历 JD 匹配分: {result.match_score}/100")

        # 1. 保存 HTML (静默)
        save_as_html(result.model_dump(), args.output)
        
        # 2. 生成 PDF
        pdf_path = args.output.replace(".html", ".pdf")
        try:
            save_as_pdf(args.output, pdf_path)
        except Exception as e:
            print(f"⚠️ PDF 生成出错: {e}")
            if "playwright" in str(e).lower():
                print("💡 请尝试运行: playwright install")

        # 尝试自动打开
        try:
            target_to_open = pdf_path if os.path.exists(pdf_path) else args.output
            if os.name == 'posix':
                os.system(f"open '{target_to_open}'")
            elif os.name == 'nt':
                os.startfile(target_to_open)
        except Exception:
            pass
            
    except Exception as e:
        print(f"❌ 运行中断: {str(e)}")

if __name__ == "__main__":
    main()
