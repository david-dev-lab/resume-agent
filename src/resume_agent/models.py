from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class ProjectExperience(BaseModel):
    project_name: str = Field(..., description="项目名称")
    role: str = Field(..., description="担任角色")
    start_date: Optional[str] = Field(None, description="开始时间，如 2023.01")
    end_date: Optional[str] = Field(None, description="结束时间，如 2023.06 或 至今")
    optimized_bullets: List[str] = Field(..., description="基于 STAR 法则优化的项目要点，必须包含量化数据")
    matched_skills: List[str] = Field(..., description="该项目用到的、与 JD 匹配的技术关键词")

class EducationExperience(BaseModel):
    school: str = Field(..., description="学校名称")
    degree: str = Field(..., description="学位，如 本科、硕士")
    major: str = Field(..., description="专业")
    start_year: str = Field(..., description="入学年份")
    end_year: str = Field(..., description="毕业年份")
    honors: Optional[List[str]] = Field(None, description="所获荣誉或奖项")

class ResumeFull(BaseModel):
    name: str = Field(..., description="姓名")
    title: str = Field(..., description="意向岗位/专业头衔")
    contact: Dict[str, str] = Field(..., description="联系方式 (phone, email, github, blog等)")
    summary: str = Field(..., description="个人总结，简练有力，突出核心优势")
    skills: List[str] = Field(..., description="技术栈列表，按熟练度排序")
    experience: List[ProjectExperience] = Field(..., description="项目经历")
    education: List[EducationExperience] = Field(..., description="教育背景")
    match_score: int = Field(..., description="简历与 JD 的匹配度评分 (0-100)")
