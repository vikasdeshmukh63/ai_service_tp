"""Pydantic models for structured job description (JD) extraction — view/DTO layer."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SalaryRangeType(StrEnum):
    """How the salary band is expressed in the JD."""

    yearly = "yearly"
    monthly = "monthly"
    weekly = "weekly"
    hourly = "hourly"
    fixed = "fixed"
    other = "other"


class WorkArrangement(StrEnum):
    """Where and how the role is performed."""

    onsite = "onsite"
    hybrid = "hybrid"
    remote = "remote"


class SkillItem(BaseModel):
    """A single skill or competency mentioned in the JD."""

    name: str = Field(
        description=(
            "Skill, tool, technology, or competency name as stated or normalized lightly."
        ),
    )
    is_mandatory: bool = Field(
        description=(
            "True if the JD marks this skill as required/mandatory; "
            "False if optional/nice-to-have."
        ),
    )


class JDExtractionSchema(BaseModel):
    """Structured data extracted from a job description document."""

    job_title: str | None = Field(
        default=None,
        description=(
            "Official job title or position name as printed in the JD "
            "(e.g. 'Senior Software Engineer')."
        ),
    )
    role: str | None = Field(
        default=None,
        description=(
            "Primary role or function (e.g. backend developer, data analyst) "
            "if distinct from title."
        ),
    )
    seniority: str | None = Field(
        default=None,
        description=(
            "Seniority level if stated (e.g. Junior, Mid, Senior, Lead, Principal, Staff)."
        ),
    )
    experience_years: int | None = Field(
        default=None,
        description=(
            "Minimum total years of experience required, as a whole number of years only."
        ),
    )
    experience_months: int | None = Field(
        default=None,
        description=(
            "Additional months beyond experience_years if the JD states a range like "
            "X years Y months; use 0 if not stated."
        ),
    )
    employment_type: str | None = Field(
        default=None,
        description=(
            "Employment type (e.g. full-time, part-time, contract, internship, freelance)."
        ),
    )
    salary_range_type: SalaryRangeType | None = Field(
        default=None,
        description=(
            "Whether salary is quoted per year, month, week, hour, as a fixed lump sum, or other."
        ),
    )
    salary_min: float | None = Field(
        default=None,
        description=(
            "Lower bound of the salary or compensation range in numeric form (no currency symbols)."
        ),
    )
    salary_max: float | None = Field(
        default=None,
        description=(
            "Upper bound of the salary or compensation range in numeric form (no currency symbols)."
        ),
    )
    work_arrangement: WorkArrangement | None = Field(
        default=None,
        description=("Whether the role is onsite, hybrid, or fully remote as stated in the JD."),
    )
    policy: str | None = Field(
        default=None,
        description=(
            "Workplace or HR policy notes called out in the JD (e.g. return-to-office, "
            "visa, background check)."
        ),
    )
    location: str | None = Field(
        default=None,
        description=(
            "Primary work location: city, state/region, country, or address line as written."
        ),
    )
    job_summary: str | None = Field(
        default=None,
        description=(
            "Short overview or 'about the role' / introduction paragraph summarizing the position."
        ),
    )
    responsibilities: list[str] = Field(
        default_factory=list,
        description=(
            "Bullet list of role responsibilities and day-to-day duties; "
            "each string is one bullet or sentence."
        ),
    )
    perks_and_benefits: list[str] = Field(
        default_factory=list,
        description=(
            "Perks, benefits, insurance, leave, equity, or wellness items; one string per item."
        ),
    )
    skills: list[SkillItem] = Field(
        default_factory=list,
        description=(
            "Skills and competencies with mandatory vs optional flag when the JD "
            "distinguishes them."
        ),
    )
    minimum_education_qualification: str | None = Field(
        default=None,
        description=(
            "Minimum education required (e.g. Bachelor's, Master's, PhD, diploma) as stated."
        ),
    )
    course_or_specialization: str | None = Field(
        default=None,
        description=(
            "Preferred or required field of study, course, or specialization "
            "(e.g. Computer Science, MBA)."
        ),
    )
    additional_requirements: list[str] = Field(
        default_factory=list,
        description=(
            "Extra requirements not covered elsewhere (certifications, travel %, language, "
            "clearance)."
        ),
    )
    status_of_jd: str | None = Field(
        default=None,
        description="Hiring status if mentioned (e.g. active, on hold, closed, urgent hiring).",
    )
    application_deadline: str | None = Field(
        default=None,
        description=(
            "Application deadline as written (date string or free text if only partial info)."
        ),
    )
    employment_start_date: str | None = Field(
        default=None,
        description="Expected start date or joining timeline if mentioned (as written in the JD).",
    )
    key_callout: str | None = Field(
        default=None,
        description=(
            "A single highlighted selling point or urgent callout the JD emphasizes "
            "(e.g. signing bonus)."
        ),
    )
    google_maps_url_of_office_location: str | None = Field(
        default=None,
        description="Google Maps URL to the office if present in the document; otherwise null.",
    )
