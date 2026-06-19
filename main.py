from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, date_tool
import time, random

#langchain core for predictable outputs

load_dotenv()

class ResearchResponse(BaseModel):
  topic: str
  summary: str
  sources: list[str]
  tools_used: list[str]

def exponentialBackoff(delay, retries):
  def decorator(func):
    def wrapper(*args, **kwargs):
      current_retry = 0
      current_delay = delay
      while current_retry < retries:
        try:
          return func(*args, **kwargs)
        except Exception as e:
          current_retry += 1
          print(f"Error: {e}. Retrying in {current_delay} seconds...")
          time.sleep(current_delay * random.uniform(0.5, 1.5))  # Adding jitter
          current_delay *= 2
      raise Exception("Max retries exceeded")
    return wrapper
  return decorator



#use gemini tbh, should be free
llm = ChatOpenAI(model="gpt-4o-mini")
llm2 = ChatAnthropic(model="Claude-3-5-sonnet-20241022") #change to latest claude haiku

parser= PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a research assistant that will help generate a research paper.
            Answer the user query and use neccessary tools. 
            Wrap the output in this format and provide no other text\n{format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())


tools = [search_tool, wiki_tool, save_tool, date_tool]
agent = create_tool_calling_agent(
  llm = llm,
  prompt = prompt,
  tools = tools
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

@exponentialBackoff(delay=2, retries=3)
def run_agent_with_retry(query):
    return agent_executor.invoke({"query": query})

query = input("What can I help you with?")
raw_response = run_agent_with_retry(query)
# print(raw_response)

try:
  structured_response = parser.parse(raw_response.get("output")[0]["text"])
  print(structured_response)
except Exception as e:
  print("Error parsing response", e, "Raw Response -", raw_response)

