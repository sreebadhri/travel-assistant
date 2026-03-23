"""Agent creation — weather, hotel, and orchestrator agents."""

from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

from .config import LLM_MODEL
from .tools import get_weather, search_hotels, book_hotel
from .prompts import WEATHER_AGENT_PROMPT, HOTEL_AGENT_PROMPT, ORCHESTRATOR_PROMPT

llm = ChatOpenAI(model=LLM_MODEL)

weather_agent = create_agent(
    llm,
    tools=[get_weather],
    system_prompt=WEATHER_AGENT_PROMPT,
    name="weather_agent",
)

hotel_agent = create_agent(
    llm,
    tools=[search_hotels, book_hotel],
    system_prompt=HOTEL_AGENT_PROMPT,
    name="hotel_agent",
)

orchestrator = create_agent(
    llm,
    tools=[],
    system_prompt=ORCHESTRATOR_PROMPT,
    name="orchestrator",
)
