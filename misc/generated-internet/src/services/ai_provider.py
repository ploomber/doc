import random
from typing import Protocol
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
from google import genai
from google.genai import types
from enum import Enum

class AIProvider(str, Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    CLAUDE = "claude"
    GEMINI = "gemini"

class AIClient(Protocol):
    """Protocol for AI clients to ensure easy provider switching"""
    async def generate_html(self, prompt: str) -> str:
        ...
 
SYSTEM_PROMPT = """You are an expert web developer tasked with generating complete, modern, and interactive HTML pages.
 
Each page must include:
- Beautiful, responsive CSS styling
- Modern, mobile-first UI/UX design
- Interactive JavaScript functionality where applicable
- Meaningful visuals (always include at least one relevant image)
- Clear, descriptive content where appropriate
- Accessibility best practices (e.g., semantic HTML, ARIA attributes)
- Fully responsive layout for all devices
- Always write detaileds text, interesting text, non-generic text
 
Design uniqueness:
- Each page must be highly individual, visually distinctive, and creatively styled. Avoid generic layouts and repeated patterns.
- Emphasize custom design choices, color schemes, layouts, and components to make every page stand out.
 
Interactivity:
- All interactive elements (e.g., links, buttons, forms) **must** include `data-action` attributes for event handling. Example:
  <button data-action="submit-form">Submit</button>
 
Output format:
- Return **only** a valid, complete HTML document, starting with `<!DOCTYPE html>` and ending with `</html>`
- **Do not** include any explanatory text, markdown, comments, or code blocks
 
IMPORTANT: The output must be production-ready, visually appealing, functionally interactive, and uniquely designed. Treat this as if you were shipping to end-users.
"""

def generate_fallback_html(message: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Generated Page</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0; padding: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; text-align: center; min-height: 100vh;
            }}
            .container {{ 
                max-width: 600px; margin: 0 auto; 
                background: rgba(255,255,255,0.1); 
                padding: 40px; border-radius: 15px; 
                backdrop-filter: blur(10px);
            }}
            .back-btn {{
                background: rgba(255,255,255,0.2);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Claude Content Generator</h1>
            <p>{message}</p>
            <p>Interaction #{random.randint(1000, 9999)}</p>
            <button class="back-btn" data-action="navigate" data-target="home">🏠 Back to Home</button>
        </div>
    </body>
    </html>
    """

class OpenAIClient:
    """OpenAI implementation of the AI client"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def generate_html(self, prompt: str) -> str:
        """Generate HTML content using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=4000,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to a basic HTML page if API fails
            return generate_fallback_html(f"Error generating content: {str(e)}")
    


class ClaudeClient:
    """Placeholder for future Claude implementation"""
    
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-20250514"):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
    
    async def generate_html(self, prompt: str) -> str:
        """Generate HTML content using Claude (not yet implemented)"""
        try:
            msg = await self.client.messages.create(
                max_tokens=10024,
                messages=[
                    {
                        "role": "user",
                        "content": SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model
            )
            return msg.content[0].text
        except Exception as e:
            # Fallback to a basic HTML page if API fails
            return generate_fallback_html(f"Error generating content: {str(e)}")
    

class GeminiClient:

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        self.client = genai.Client(api_key=api_key)
        self.model = model

    async def generate_html(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT
            ),
            contents=prompt,
        )
        return response.text
