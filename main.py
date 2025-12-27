from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import asyncio
import os

os.environ["GOOGLE_API_KEY"] = "AIzaSyA2kzjhfglQU1i7E7ykKRPxUhEO6yENts0"

def file_create(file_name: str, content: str) -> str:
    """Creates a file with the given name and content."""
    with open(file_name, 'w') as file:
        file.write(content)
    return f"File '{file_name}' created successfully."

root_agent = Agent(
    model="gemini-2.5-flash", 
    name="chat_agent",
    description=(
        "A helpful assistant agent that can answer questions and provide "
        "information based on its training knowledge."
    ),
    instruction="""
      You are a helpful assistant. Answer user queries to the best of your 
      ability using your knowledge. Be concise and accurate in your responses.
    """,
    tools=[file_create]
)

async def main():
    # Create session service
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="chat_app",
        user_id="user_001",
        session_id="session_001"
    )
    
    # Create runner
    runner = Runner(
        agent=root_agent,
        app_name="chat_app",
        session_service=session_service
    )
    
    # Create user message
    user_content = types.Content(
        role="user",
        parts=[types.Part(text="Create a file named 'test.txt' with content 'Hello World'")]
    )
    
    # Run agent and collect responses
    for event in runner.run(
        user_id="user_001",
        session_id="session_001",
        new_message=user_content
    ):
        if hasattr(event, "content") and event.content:
            for part in event.content.parts:
                print(part.text)

if __name__ == "__main__":
    asyncio.run(main())