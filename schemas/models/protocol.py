"""
Protocol Models.

Defines the structured data envelopes exchanged between agents in the system
(e.g., Research Findings, Feedback, Content Articles).
"""

from typing import Literal

from pydantic import BaseModel, Field


class ResearchFindings(BaseModel):
    """Structured output from the Researcher agent."""

    topic: str = Field(description="The topic that was researched.")
    summary: str = Field(description="A comprehensive summary of the findings.")
    sources: list[str] = Field(description="List of URLs or sources used.")


class JudgeFeedback(BaseModel):
    """Structured feedback from the Judge agent."""

    status: Literal["pass", "fail"] = Field(
        description="Whether the research is sufficient ('pass') or needs more work ('fail')."
    )
    feedback: str = Field(
        description="Detailed feedback on what is missing or needs clarification if status is 'fail'. If 'pass', a brief confirmation."
    )


class ContentSection(BaseModel):
    """A section of content with optional visual direction."""

    heading: str = Field(description="The heading of the section.")
    content: str = Field(description="The main text content of the section.")
    image_prompt: str | None = Field(
        default=None,
        description="A detailed prompt for generating an image relevant to this section. Use 'Subject + Action + Context + Style'.",
    )
    image_path: str | None = Field(
        default=None,
        description="Path to the generated image file. Populated by the Orchestrator.",
    )


class ContentArticle(BaseModel):
    """Structured output from the Content Builder agent."""

    title: str = Field(description="The title of the article.")
    target_audience: str = Field(description="The intended audience for this content.")
    sections: list[ContentSection] = Field(description="List of content sections.")


class CustomerServiceResponse(BaseModel):
    """Structured output from the Customer Service agent."""

    message: str = Field(description="The response message to the user.")
    intent: Literal["chat", "gathering_info", "research_request"] = Field(
        description="The intent. 'chat' for general talk. 'gathering_info' when asking clarifying questions. 'research_request' ONLY when all requirements (topic, tone, type) are clear."
    )
    topic: str | None = Field(
        default=None,
        description="The topic to research. Required for 'research_request'.",
    )
    content_type: Literal["Article", "Social Post", "Course"] | None = Field(
        default=None,
        description="The type of content to create. Required for 'research_request'.",
    )
    tone: Literal["Professional", "Fun", "Academic"] | None = Field(
        default=None, description="The desired tone. Required for 'research_request'."
    )
    target_audience: str | None = Field(
        default=None, description="The target audience. Optional but helpful."
    )



