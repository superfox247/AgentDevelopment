from pydantic import BaseModel, Field

class ResearchFindings(BaseModel):
    topic: str = Field(..., description="The research topic.")
    summary: str = Field(..., description="Summary of the findings.")
    sources: list[str] = Field(default_factory=list, description="List of sources.")
