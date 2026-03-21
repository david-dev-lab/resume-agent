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

# 指定文件和模型
resume-run --thoughts data/raw_thoughts.md --jd data/target_jd.txt --output output/my_resume.html --model deepseek-chat
```

## 项目结构

```
resume-agent/
├── src/resume_agent/       # 核心逻辑
│   ├── main.py             # CLI 入口
│   ├── core.py             # Agent 与 LLM 流程
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
- OpenAI / DeepSeek API
