# 简历 Agent

通过 AI 提取 JD 关键词并自动重写简历。

## 快速开始

```bash
# 1. 安装（含开发依赖）
pip install -e ".[dev]"

# 2. 配置 .env（参考 .env.example）
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 3. 安装 Playwright 浏览器（PDF 生成需要）
playwright install chromium

# 4. 运行
resume-run
```

## 使用方式

```bash
# 使用默认示例数据（data/raw_thoughts.md + data/target_jd.txt）
resume-run

# 指定文件、模型和排版模板
resume-run --thoughts data/raw_thoughts.md --jd data/target_jd.txt --output output/my_resume.html --model deepseek-chat --template modern_two_column.html
```

## 可用模板

本项目支持多种简历排版模板（感谢 [Resume-Matcher](https://github.com/srbhr/Resume-Matcher) 提供的开源 CSS 设计灵感）：
- `swiss_single_column.html`: **默认**瑞士设计风格单列模板
- `swiss_two_column.html`: 瑞士设计风格双列模板（排版紧凑）
- `modern_single_column.html`: 现代风格单列模板（带彩色下划线）
- `modern_two_column.html`: 现代风格双列模板（推荐）

## 项目结构

```
resume-agent/
├── src/resume_agent/       # 核心逻辑
│   ├── main.py             # CLI 入口
│   ├── core.py             # 对外门面（调用编排层）
│   ├── orchestrator.py     # build_resume 确定性流程；create_resume_agent 可选
│   ├── steps.py            # draft / critique / refine 共用实现
│   ├── textutil.py         # 命令行单行截断
│   ├── context.py          # ResumeWorkspace / StatusCallback
│   ├── tools/              # 各 Tool 独立模块（draft / critique / refine）
│   ├── model_factory.py    # OpenAI 兼容模型（DeepSeek 等）
│   ├── resume_prompts.py   # ResumePrompts：YAML 指令加载
│   ├── models.py           # Pydantic 数据模型
│   ├── utils.py            # HTML/PDF 渲染与文件工具
│   ├── prompts/            # Prompt 配置
│   └── templates/          # Jinja2 简历模板
├── tests/                  # 单元测试
├── data/                   # 示例 JD 与原始思绪
└── pyproject.toml          # 项目配置与依赖
```

## 依赖

- Python 3.12+
- Pydantic V2
- [Pydantic AI](https://github.com/pydantic/pydantic-ai)（Agent + Tool 编排，可观测、可扩展）
- OpenAI 兼容 API（默认 DeepSeek，见 `.env.example`）

## 致谢

**Acknowledgments:**
The resume HTML templates (Tailwind CSS designs) used in this project are inspired by and ported from [Resume-Matcher](https://github.com/srbhr/Resume-Matcher) (licensed under Apache 2.0).
