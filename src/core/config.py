from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl

class Settings(BaseSettings):
    # Jira Settings
    jira_url: str
    jira_email: str
    jira_api_key: str
    
    # GitLab Settings (Optional for now, but ready)
    gitlab_url: str = "https://gitlab.com"
    gitlab_token: str = ""
    
    # LangChain/LangSmith
    langchain_project: str = "mcp-multi-gateway"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
