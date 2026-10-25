from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from tool import tools
from instructions import SYSTEM_PROMPT
from dotenv import load_dotenv
import os

load_dotenv()

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

agent = create_agent(
    model=model,
    tools=tools,
    system_prompt=SYSTEM_PROMPT,
)

result = agent.invoke(
    {"messages":[{"role": "user", "content": "How long is a year on Mars?"}]}
)

print(result["messages"][-1].content)