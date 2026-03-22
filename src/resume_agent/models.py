from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class LayoutStatus(str, Enum):
    """HTML 渲染相对 A4 单页的版面状态（供感知-反馈循环使用）。"""

    OVERFLOW = "OVERFLOW"
    UNDERFLOW = "UNDERFLOW"
    PERFECT = "PERFECT"


class WorkProject(BaseModel):
    project_name: str = Field(..., description="项目名称")
    role: str = Field(..., description="担任角色")
    start_date: Optional[str] = Field(None, description="开始时间，如 2023.01")
    end_date: Optional[str] = Field(None, description="结束时间，如 2023.06 或 至今")
    optimized_bullets: List[str] = Field(
        ...,
        description="项目要点：按 STAR 逻辑内化写作，每条为融合后的独立 bullet，禁止出现 Situation:/Task:/Action:/Result: 等标签字样；尽量含可核实量化数据",
    )
    matched_skills: List[str] = Field(..., description="该项目用到的、与 JD 匹配的技术关键词")


class EducationEntry(BaseModel):
    school: str = Field(..., description="学校名称")
    degree: str = Field(..., description="学位，如 本科、硕士")
    major: str = Field(..., description="专业")
    start_year: str = Field(..., description="入学年份")
    end_year: str = Field(..., description="毕业年份")
    honors: Optional[List[str]] = Field(None, description="所获荣誉或奖项")


class Resume(BaseModel):
    name: str = Field(..., description="姓名")
    title: str = Field(..., description="意向岗位/专业头衔")
    contact: Dict[str, str] = Field(..., description="联系方式 (phone, email, github, blog等)")
    summary: str = Field(..., description="个人总结，简练有力，突出核心优势")
    skills: List[str] = Field(..., description="技术栈列表，按熟练度排序")
    experience: List[WorkProject] = Field(..., description="项目经历")
    education: List[EducationEntry] = Field(..., description="教育背景")
    match_score: int = Field(..., description="简历与 JD 的匹配度评分 (0-100)")


class ResumeCritique(BaseModel):
    critique: str = Field(..., description="针对简历的简短批评意见，指出哪里没写好，哪里缺少量化")
    missing_keywords: List[str] = Field(..., description="简历中遗漏的 JD 关键技术词")
    score: int = Field(..., description="当前简历质量评分 (0-100)")
    needs_revision: bool = Field(..., description="是否需要重写 (分数<85或有重大遗漏时为True)")
