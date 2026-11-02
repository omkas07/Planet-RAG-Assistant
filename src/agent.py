from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph import StateGraph, MessagesState, START, END 
from tool import Tools
from instructions import PLANETS_PROMPT, DATABASE_PROMPT, ROUTER_PROMPT
from dotenv import load_dotenv
from typing import Literal
import os

load_dotenv()

class State(MessagesState):
    question: str
    route: str

model = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

planets_agent = create_agent(
    model=model,
    tools=[Tools.search_planets],
    system_prompt=PLANETS_PROMPT
)

database_agent = create_agent(
    model = model,
    tools=[Tools.list_tables, Tools.describe_table],
    system_prompt=DATABASE_PROMPT,
)

def classify(state: State):
    question = state["messages"][-1].content
    verdict = model.invoke([
        {"role":"system", "content" : ROUTER_PROMPT},
        {"role": "user", "content" : question}]).content.strip().upper()

    route = "database" if verdict.startswith("DATABASE") else "planets"
    return {"question" : question, "route" : route}

def pick(state: State) -> Literal["planets", "database"]:
    return state["route"]

builder = StateGraph(State)
builder.add_node("classify", classify)
builder.add_node("planets", planets_agent)
builder.add_node("database", database_agent)

builder.add_edge(START, "classify")
builder.add_conditional_edges("classify", pick)
builder.add_edge("planets", END)
builder.add_edge("database", END)

graph = builder.compile()

if __name__ == "__main__":
    questions = [
        "Why is Venus so hot?",
        "Which planet is the largest?",
    ]
    for q in questions:
        result = graph.invoke({"messages": [{"role": "user", "content": q}]})
        print(f"\n=== {result['question']} ===")
        print("route: ", result["route"])
        print("answer:", result["messages"][-1].content)