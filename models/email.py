from pydantic import BaseModel, Field

class EmailContent(BaseModel):
    """Extracted email data
    
    Keyword arguments:
    argument -- description
    Return: return_description
    """
    
    email_address: str = Field(description='The email address of the sender of the email')
    host_domain: str = Field(description='The website of the organisation the sender originates from')
    subject: str = Field(description='The subject of the email')
    body: str = Field(description='The body and content of the email')
    links: list[str] = Field(description='Relevant links to websites that might require our interaction')
    headers: list[str] = Field(description='Email headers')
    
