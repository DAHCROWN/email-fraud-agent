from pydantic import BaseModel, Field


class EmailParseInput(BaseModel):
    content: str = Field(description="The copied email text")

