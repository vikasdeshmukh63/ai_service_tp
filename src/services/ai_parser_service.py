"""JD parsing via LangChain + OpenAI structured output."""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.core.config import settings
from src.views.jd_schema import JDExtractionSchema


def extract_jd_fields(pdf_text: str) -> JDExtractionSchema:
    """
    Parse plain text from a JD PDF into a structured schema using GPT-4o.
    Fields not mentioned in the text should remain null or empty lists.
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
            (
                "system",
                (
                    "You are an expert ATS and recruiting document parser. "
                    "Extract structured data from the job description text exactly according to "
                    "the schema. "
                    "Use null for any field not clearly stated. "
                    "Use empty lists where no items apply. "
                    "Normalize numbers (salary, years) without currency symbols in numeric fields. "
                    "Preserve wording for dates and deadlines when given as free text."
                ),
            ),
            (
                "human",
                "Job description text:\n\n{jd_text}",
            ),
        ]
    )

    chain = prompt | structured_llm
    result = chain.invoke({"jd_text": pdf_text})
    return result
