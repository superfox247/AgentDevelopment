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


class CourseModule(BaseModel):
    """A single module within a course."""
    title: str = Field(description="The title of the module.")
    content: str = Field(description="The educational content of the module.")


class CourseContent(BaseModel):
    """Structured output from the Content Builder agent."""
    title: str = Field(description="The title of the course.")
    modules: list[CourseModule] = Field(description="List of course modules.")


class CustomerServiceResponse(BaseModel):
    """Structured output from the Customer Service agent."""
    message: str = Field(description="The response message to the user.")
    intent: Literal["chat", "research_request"] = Field(
        description="The intent of the user. 'chat' for greetings/questions, 'research_request' if they want a course created."
    )
    topic: str | None = Field(
        default=None,
        description="The topic to research if intent is 'research_request'. None otherwise."
    )


class ImageGenerationRequest(BaseModel):
    """Request to generate an image from a prompt."""
    prompt: str = Field(description="The text prompt to generate an image from.")


class ImageGenerationResponse(BaseModel):
    """Response containing the path to the generated image."""
    image_path: str = Field(description="The local file path to the generated image artifact.")
