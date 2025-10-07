import os
from dotenv import load_dotenv

from openai import OpenAI 
from anthropic import Anthropic

load_dotenv()

OPENAI_MODEL = "gpt-4o"
ANTHROPIC_MODEL = "claude-3-5-sonnet-20240620"

def initialize_clients():
    """Initialize OpenAI and Anthropic clients using API keys from environment variables."""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Check if API keys are available
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        if not anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        openai_client = OpenAI(api_key=openai_api_key)
        anthropic_client = Anthropic(api_key=anthropic_api_key)
        
        print("OpenAI and Anthropic clients initialized successfully.")
        return openai_client, anthropic_client
        
    except ValueError as ve:
        print(f"Configuration error: {ve}")
        raise
    except Exception as e:
        print(f"Error initializing clients: {e}")
        raise

if __name__ == "__main__":
    openai_client, anthropic_client = initialize_clients()