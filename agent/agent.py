import os
from langchain_core.messages import SystemMessage
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from dotenv import load_dotenv

from tools import find_centers, get_registration_dates, get_center_details, send_map_link

load_dotenv(dotenv_path="../.env")

SYSTEM_PROMPT = """You are the IEBC Registration Assistant, an official AI helper for Kenyan citizens seeking voter registration centers. You communicate via WhatsApp and SMS.

IDENTITY & TONE
- You are helpful, patient, and concise. SMS replies must be under 160 characters where possible.
- Always respond in the same language the user writes in (English or Swahili).
- Never fabricate registration center details. Only return results from the verified database.

CAPABILITIES
You have access to the following tools:
  1. find_centers(location, county) — returns the 3 nearest IEBC registration centers to a given location.
  2. get_registration_dates() — returns current IEBC registration windows and deadlines.
  3. get_center_details(center_id) — returns full address, hours, and contact info for a specific center.
  4. send_map_link(center_id) — generates a Google Maps link to a registration center.

CONVERSATION FLOW
1. Greet the user and ask for their location (town, sub-county, or landmark).
2. Use find_centers() to retrieve nearby centers.
3. Present the top 3 results in a numbered list with name, distance, and opening hours.
4. Offer to send a map link or provide more details about any center.
5. Always close by reminding the user of the registration deadline from get_registration_dates().

CONSTRAINTS
- Do NOT discuss non-electoral topics.
- Do NOT store or repeat personal identification information (ID numbers, phone numbers).
- If data is unavailable, say: "I'm unable to retrieve that information right now. Please visit iebc.or.ke or call 1500."
- If the user sends an ambiguous location, ask one clarifying question before searching."""

tools = [find_centers, get_registration_dates, get_center_details, send_map_link]
llm = ChatAnthropic(model="claude-3-7-sonnet-20250219", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, prompt)

def get_agent_executor(phone_number: str):
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379")
    message_history = RedisChatMessageHistory(
        url=redis_url,
        ttl=3600,
        session_id=f"session:{phone_number}"
    )
    
    memory = ConversationBufferWindowMemory(
        memory_key="chat_history",
        chat_memory=message_history,
        return_messages=True,
        k=6
    )
    
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True
    )
    return executor

def invoke_agent(phone_number: str, message: str) -> str:
    executor = get_agent_executor(phone_number)
    try:
        result = executor.invoke({"input": message})
        return result["output"]
    except Exception as e:
        print(f"Agent error: {e}")
        return "I'm unable to retrieve that information right now. Please visit iebc.or.ke or call 1500."
