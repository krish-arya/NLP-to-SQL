from schema_extractor import extract_schema, render_schema_text
from vector_store import create_schema_store, query_schema_store
from agent_runner import build_agent

CONNECTION_STRING = "sqlite:///example.db"

if __name__ == "__main__":
    print("\n=== Auto-SQL Agent with Vector Memory and Multilingual Conversational Support ===")

    # 1. Extract and render schema 
    print("🔎 Extracting database schema...")
    schema = extract_schema(CONNECTION_STRING)
    schema_text = render_schema_text(schema)
    chunks = schema_text.split("\n\n")
    print("✅ Schema extraction complete.")

    # 2. Store in VectorDB
    print("📦 Storing schema in vector memory...")
    collection = create_schema_store(chunks)
    print("✅ Vector memory ready.")

    # 3. Build Agent with Memory
    print("🤖 Initializing multilingual conversational agent...")
    agent = build_agent()
    print("✅ Agent ready!\n")

    # 4. Interactive Conversation Loop
    print("💬 You can now ask questions in Hindi or English!")
    print("💡 The agent will remember prior context for follow-ups.")
    print("🔚 Type 'exit' or 'quit' to end the session.\n")

    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break

        # 5. Retrieve relevant schema context for this question
        top_chunks = query_schema_store(collection, question)
        schema_context = "\n".join(top_chunks)

        # 6. Augment question with retrieved schema
        full_input = f"{question}\n\nSCHEMA CONTEXT:\n{schema_context}"

        # 7. Invoke the agent
        try:
            response = agent.invoke({"input": full_input})
            print("\nAgent:", response, "\n")
            import re

            agent_output = response['output'] if isinstance(response, dict) else response

            # Extract SQL query from the agent output
            sql_match = re.search(r"```sql\n(.*?)```", agent_output, re.DOTALL)
            if sql_match:
                sql_query = sql_match.group(1).strip()
                print("✅ SQL to run:\n", sql_query)
                from tools import execute_sql_tool
                import os
                connection_string = os.getenv("DATABASE_URL")  # adjust this key
                result_text =execute_sql_tool(connection_string, sql_query)
                print("🗣️ Answer:\n", result_text)


        except Exception as e:
            print("\n❌ [ERROR]:", str(e), "\n")