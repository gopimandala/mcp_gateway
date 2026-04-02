# brain/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import HttpUrl


class BrainSettings(BaseSettings):
    # Brain Server Port (AI Orchestration)
    brain_port: int = 9000
    
    # Guardrail Server Port (Content Safety)
    guardrail_port: int = 9010
    
    # MCP Gateway URL (HTTP Wrapper)
    mcp_gateway_url: str = "http://localhost:8080"
    
    # OpenAI Configuration
    openai_key: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


brain_settings = BrainSettings()