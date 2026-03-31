"""JD parsing via LangChain + OpenAI structured output."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.views.jd_schema import JDExtractionSchema

_SYSTEM_PROMPT = """You are an expert recruiter and ATS parser. Your job is to extract
**as much structured information as possible** from the job description (JD) text.

## Principles
- **Fill fields aggressively** when the JD reasonably implies or states the value. Do not leave
  fields null out of caution if a normal recruiter would infer them from the text.
- Only use null or empty lists when the information is truly absent or unknowable from this text.
- **Infer** role, seniority, work arrangement, and experience ranges from titles, bullet lists,
  and common hiring language when explicit labels are missing.

## Experience
- Parse ranges: "3-6 years", "3–6 yrs", "3 to 5 years" -> experience_min_years / experience_max_years.
- "5+ years", "at least 5 years" -> experience_min_years=5, experience_max_years=null.
- Set experience_years to the same as experience_min_years when you use a range (for compatibility).

## Compensation
- salary_currency: INR for ₹, LPA, lakhs, crores (India); USD for $; EUR/GBP when stated.
- Normalize to **annual** numeric amounts in salary_min / salary_max (no symbols):
  - India: 12 LPA or 12–22 LPA = 12 to 22 **lakhs per year** -> use 1200000 and 2200000 (or 12000000
    if the JD clearly means 12 crore; use context).
  - "50k per month" -> monthly type and convert to annual if salary_range_type is yearly by multiplying by 12.
- salary_range_type: match how the JD quotes pay (yearly for LPA/CTC annual, monthly for per-month).

## Work location & arrangement
- work_arrangement: onsite vs hybrid vs remote from phrases (WFH, hybrid, remote-first, on-site).
- policy: capture hybrid/remote **details** (e.g. "3 days office, 2 days remote", "3 days/week WFH").
- locations: separate list entries for country, city/region when given (e.g. "India", "Mumbai, Maharashtra").
  You may also set location to a short combined string if useful.

## Job content
- job_summary: opening paragraph / "about the role" / overview only — not the full bullets.
- responsibilities: one bullet per string; include **all** substantive duty bullets from the JD.
- perks_and_benefits: each perk/benefit as its own string; keep text from the JD where possible.

## Skills
- Extract **every** skill, tool, framework, and domain competency (including soft skills if listed).
- is_mandatory=true if the JD says required, must-have, mandatory, or lists under "Required";
  false for nice-to-have, preferred, bonus, optional.
- If a single list mixes both, use context (must before nice-to-have sections) or default mandatory=true
  for core stack in the title.

## Other fields
- minimum_education_qualification / course_or_specialization: fill when degree or field is stated.
- additional_requirements: certifications, notice period, language, travel, portfolio links, joining timeline.
- key_callout: application method restrictions, "do not email", urgent hiring, or one standout banner message.
- application_deadline / employment_start_date: copy as written if dates appear.
- status_of_jd: if hiring status or draft/published is mentioned.
- google_maps_url_of_office_location: only if a maps or Google URL appears in the text.

Return valid JSON matching the schema. Use empty lists for list fields with no items."""


def extract_jd_fields(pdf_text: str) -> JDExtractionSchema:
    """
    Parse plain text from a JD PDF into a structured schema using GPT-4o.
    Fields not present in the text should remain null or empty lists.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set; cannot extract JD fields.")

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=settings.openai_api_key,
    )
    structured_llm = llm.with_structured_output(JDExtractionSchema)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", _SYSTEM_PROMPT),
            (
                "human",
                "Job description text:\n\n{jd_text}",
            ),
        ]
    )

    chain = prompt | structured_llm
    result = chain.invoke({"jd_text": pdf_text})
    return result
