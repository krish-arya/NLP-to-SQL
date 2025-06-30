from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.memory import ConversationBufferMemory

from tools import generate_sql_tool, execute_sql_tool

def build_agent():
    """
    Builds a LangChain AgentExecutor with conversation memory,
    multilingual-aware system prompt, and Gemini 2.0 as LLM.
    """
    # Initialize Gemini Chat Model
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-pro")

    # Define tools available to the agent
    tools = [generate_sql_tool, execute_sql_tool]

    # Prompt with system instructions and conversation memory placeholder
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
        ("human", "{input}")
    ])

    # Conversation memory to hold past user-agent messages
    memory = ConversationBufferMemory(
        return_messages=True,
        memory_key="chat_history"
    )

    # Assemble the agent
    agent = create_openai_functions_agent(
        llm=llm,
        tools=tools,
        prompt=prompt
    )

    # Return an executable AgentExecutor with memory
    return AgentExecutor(agent=agent, tools=tools, memory=memory)
