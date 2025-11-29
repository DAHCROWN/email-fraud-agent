from pydantic import BaseModel

class EmailReport(BaseModel):
    credibility_percentage: str


class LinkEvaluation(BaseModel):
    link: str
    origin: str
    evalution: str
    