# 简历 Agent

通过 AI 提取 JD 关键词并自动重写简历。

## 快速开始

```bash
# 确保已配置 .env 中的 API Key（OPENAI_API_KEY 或 DEEPSEEK_API_KEY）
python main.py
```

## 项目结构

```
resume-agent/
├── src/resume_agent/   # 核心逻辑
├── tests/              # 单元测试
├── data/               # 示例 JD 与简历
└── main.py             # 启动入口
```

## 使用方式

```bash
# 使用默认示例数据
python main.py

# 指定路径（后续支持）
python main.py --resume data/base_resume.md --jd data/target_jd.txt
```

## 依赖

- Python 3.12+
- Pydantic V2
- OpenAI / DeepSeek API
