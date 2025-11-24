from google.adk.agents.llm_agent import Agent, LlmAgent
from agent import email_parser_agent
from models.email import EmailContent
from tools.email_parser_tool import parse_eml_file


email_parser_agent = LlmAgent(
    model="gemini-2.0-flash",
    name="email_parser_agent",
    description="Parses email files (.eml format) and extracts structured email data including sender, subject, body, links, and headers.",
    instruction="""You are an email parsing agent that extracts structured information from email files. 
    When given an email file path, use the parse_eml_file tool to extract:
    - Email address of the sender
    - Host domain of the sender
    - Subject line
    - Email body content
    - All links found in the email
    - All email headers
    
    Return the parsed email data in the structured EmailContent format.""",
    # input_schema=EmailParseInput,
    output_schema=EmailContent,
    tools=[parse_eml_file]
)

root_agent = Agent(
    model='gemini-2.0-flash', #'gemini-3-pro-preview',
    name='email_fraud_agent',
    description="Checks User email and flags potential phishing emails and fraud emails",
    instruction="You are a helpful email fraud detection agent that checks user email and flags potential phishing emails and fraud emails",
    tools=[parse_eml_file],
    sub_agents=[email_parser_agent]
)