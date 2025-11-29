# rag/models.py

from pydantic import BaseModel, Field
from typing import Optional

class EmailRecord(BaseModel):
    """
    Schema for normalized email dataset rows.
    Adjust this model whenever your CSV structure evolves.
    """
    sender: str = Field(..., description="Sender email address")
    receiver: str = Field(..., description="Recipient email address")
    date: Optional[str] = Field(None, description="Email date string")
    subject: Optional[str] = Field(None, description="Email subject")
    body: str = Field(..., description="Full email body text")
    urls: Optional[int] = Field(0, description="Total number of embedded URLs")
    label: Optional[str] = Field(None, description="Spam/Not Spam or category label")

class NigerianFraudDataset(BaseModel):
    """
    Schema for Nigerian Fraud Dataset
    """
    sender: str = Field(..., description="Sender email address")
    receiver: str = Field(..., description="Recipient email address")
    date: Optional[str] = Field(None, description="Email date string")
    subject: Optional[str] = Field(None, description="Email subject")
    body: str = Field(..., description="Full email body text")
    urls: Optional[int] = Field(0, description="Total number of embedded URLs")
    label: Optional[str] = Field(None, description="Spam/Not Spam or category label")

class SpamAssasinDataset(BaseModel):
    """
    Schema for the Spam Assasin dataset
    """
    sender: str = Field(..., description="Sender email address")
    receiver: str = Field(..., description="Recipient email address")
    date: Optional[str] = Field(None, description="Email date string")
    subject: Optional[str] = Field(None, description="Email subject")
    body: str = Field(..., description="Full email body text")
    urls: Optional[int] = Field(0, description="Total number of embedded URLs")
    label: Optional[str] = Field(None, description="Spam/Not Spam or category label")


class LingDataset(BaseModel):
    """
    Schema for the Ling Dataset
    """
    subject: Optional[str] = Field(None, description="Email subject")
    body: str = Field(..., description="Full email body text")
    label: Optional[str] = Field(None, description="Spam/Not Spam or category label")