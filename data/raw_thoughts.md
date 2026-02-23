# 某匿名极客的零散笔记 (测试用)

## 身份信息
我叫 Alex，一名在后端领域摸爬滚打了三年的开发者。GitHub ID 是 "anonymous-dev-2026"。
联系方式：dev-test@example.com，电话保密。

## GIS 空间计算项目经历 (之前的核心项目)
以前负责过一个“海量地理围栏计算平台”。
核心难点是处理百万级的 Tile 瓦片数据和复杂的多边形边界。
我当时选用了 GeoPandas 和 Shapely 库来做空间的布尔运算（交集、并集）。
最初版本性能很差，因为 Python 单线程做拓扑计算太慢了。
后来我重构了底层逻辑，引入了 R-tree 空间索引，并把耗时运算推到了 PostGIS 数据库侧，
利用 GiST 索引优化查询。重构后整体吞吐量提升了大概 300% 左右。
这个东西主要解决了地图测绘数据的自动化聚合问题。

## 关于当前的 AI Agent 框架开发
目前正在手搓一个 Resume-Agent 开源项目。
目标是 1.5 天产出 MVP，主打“快准狠”。
技术栈选了 Python 3.12 + Pydantic V2，用 Pydantic 主要是为了强校验 LLM 的输出。
接入了 DeepSeek-V3 接口。
项目采用了标准的 src/ 布局，完全兼容 pip install -e .。
我折腾了很久的 System Prompt，主要是为了让 AI 能理解 STAR 法则。
输出端我直接写了一套 Jinja2 模板，配合 Tailwind CSS，生成的简历看起来很有硅谷范儿。

## 其他技能碎片
熟练使用 Git 做分支管理，拒绝乱用 rebase。
开发环境是 Mac + Miniconda3，比较喜欢这种轻量级的包管理。
对 LLM 的 Function Calling 和结构化输出（JSON Mode）有实战经验。
之前的技术头儿对代码规范要求极高（哪怕是一个变量命名都要反复推敲），这让我养成了写 Clean Code 的习惯。
学历是统招本科，计算机科学与技术专业。