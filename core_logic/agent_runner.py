from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.memory import ConversationBufferMemory
from tools import generate_sql_tool, execute_sql_tool
from dotenv import load_dotenv
import os

load_dotenv()
google_api_key = os.getenv("GOOGLE_API")

def build_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=google_api_key
    )
    tools = [generate_sql_tool, execute_sql_tool]
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
You are a self-healing SQL generation agent who understands multiple languages, including Hindi and other Indian languages.
Your capabilities:
- Accept USER QUESTIONS in any Indian language (e.g., Hindi, Tamil, Bengali).
- Retrieve relevant database schema context.
- Plan and generate a valid SQL query in English.
- Execute SQL on the connected database.
- If there's an error, fix it and retry.
- Maintain context across multiple conversation turns to resolve references and follow-ups.
Be careful, thorough, and multilingual-aware.
        """),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        ("ai", "{agent_scratchpad}")
    ])
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(agent=agent, tools=tools, memory=memory)
