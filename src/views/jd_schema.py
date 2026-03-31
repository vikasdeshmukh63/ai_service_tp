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
            "Job function or track (e.g. Full-stack Developer, Backend Engineer, Data Analyst). "
            "Infer from title and stack when implied (e.g. MERN title -> Full-stack Developer)."
        ),
    )
    seniority: str | None = Field(
        default=None,
        description=(
            "Normalized seniority: Intern, Junior, Mid-level, Senior, Lead, Principal, Staff. "
            "Infer from title ('Senior X'), years of experience, or explicit wording."
        ),
    )
    experience_min_years: int | None = Field(
        default=None,
        description=(
            "Minimum years of experience in a stated range (e.g. 3 from '3-6 years' or "
            "'3+ years'). Whole years only."
        ),
    )
    experience_max_years: int | None = Field(
        default=None,
        description=(
            "Maximum years in a stated range (e.g. 6 from '3-6 years'). "
            "If only a minimum is stated (e.g. '5+ years'), set max to null."
        ),
    )
    experience_years: int | None = Field(
        default=None,
        description=(
            "Legacy single minimum when no explicit range exists; prefer experience_min_years. "
            "If you output min/max, you may set this equal to experience_min_years."
        ),
    )
    experience_months: int | None = Field(
        default=None,
        description=(
            "Additional months beyond whole years if the JD states 'X years Y months'; else null."
        ),
    )
    employment_type: str | None = Field(
        default=None,
        description=(
            "Employment type (e.g. full-time, part-time, contract, internship, freelance)."
        ),
    )
    salary_currency: str | None = Field(
        default=None,
        description=(
            "ISO-like currency code for compensation (INR, USD, EUR, GBP). "
            "Infer from symbols (₹, $) or text (INR, USD, LPA in India context)."
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
            "Lower bound in numeric form (annual base currency units). "
            "For India: convert LPA/lakhs to full numbers (12 LPA -> 1200000, 12-22 LPA -> min 1200000)."
        ),
    )
    salary_max: float | None = Field(
        default=None,
        description=(
            "Upper bound in same units as salary_min. 22 LPA -> 2200000."
        ),
    )
    work_arrangement: WorkArrangement | None = Field(
        default=None,
        description=("Whether the role is onsite, hybrid, or fully remote as stated in the JD."),
    )
    policy: str | None = Field(
        default=None,
        description=(
            "Hybrid/remote policy or WFH rules (e.g. '3 days/week in office', "
            "'2 days remote') and other workplace rules; also visa/background if prominent."
        ),
    )
    locations: list[str] = Field(
        default_factory=list,
        description=(
            "All distinct location strings: country, city/state, or site name as separate "
            "entries when multiple (e.g. 'India', 'Mumbai, Maharashtra')."
        ),
    )
    location: str | None = Field(
        default=None,
        description=(
            "Optional single-line summary of primary location; prefer filling locations list."
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
            "One line the JD highlights for candidates: application instructions "
            "(e.g. apply only on portal, no LinkedIn), urgency, or top perk/benefit callout."
        ),
    )
    google_maps_url_of_office_location: str | None = Field(
        default=None,
        description="Google Maps URL to the office if present in the document; otherwise null.",
    )
