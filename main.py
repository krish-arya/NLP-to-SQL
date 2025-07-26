from schema_extractor import extract_schema, render_schema_text
from vector_store import create_schema_store, query_schema_store
from agent_runner import build_agent
from llm_language_router import route_query
from self_healing_vector_db import store_error_pattern, search_similar_errors, prompt_gemini_with_error

import re
import os

CONNECTION_STRING = "sqlite:///example.db"

if __name__ == "__main__":
    print("\n=== Auto-SQL Agent with Vector Memory and Self-Healing ===")
    print("Extracting database schema...")
    schema = extract_schema(CONNECTION_STRING)
    schema_text = render_schema_text(schema)
    chunks = schema_text.split("\n\n")
    print("Schema extraction complete.")

    print("Storing schema in vector memory...")
    collection = create_schema_store(chunks)
    print("Vector memory ready.")

    print("Initializing multilingual conversational agent...")
    agent = build_agent()
    print("Agent ready!\n")

    print("You can now ask questions in Hindi or English!")
    print("The agent will remember prior context for follow-ups.")
    print("Type 'exit' or 'quit' to end the session.\n")
    
    while True:
        question = input("You: ").strip()
        if question.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break


        english_query = route_query(question)

        top_chunks = query_schema_store(collection, english_query)
        schema_context = "\n".join(top_chunks)

        full_input = f"{english_query}\n\nSCHEMA CONTEXT:\n{schema_context}"

        try:
            response = agent.invoke({"input": full_input})

            agent_output = response['output'] if isinstance(response, dict) else response
            print("\nAgent:", agent_output, "\n")
            sql_match = re.search(r"``````", agent_output, re.DOTALL)
            if sql_match:
                sql_query = sql_match.group(1).strip()
                print("SQL to run:\n", sql_query)
                from tools import execute_sql_tool
                db_url = os.getenv("DATABASE_URL", CONNECTION_STRING)
                try:
                    result_text = execute_sql_tool(db_url, sql_query)
                    print("Answer:\n", result_text)
                except Exception as e:
                    # === ERROR HANDLING AND SELF-HEALING ===
                    print("\n❌ [SQL ERROR]:", str(e), "\n")
                    # Store error pattern in vector DB, search for similar
                    error_msg = str(e)
                    # Save full schema snapshot
                    sim_errors = search_similar_errors(schema_text, sql_query, error_msg, english_query)
                    best_case = sim_errors[0]['meta'] if sim_errors else None
                    # If a past fix exists, supply for bootstrapping
                    fix_sql = best_case['fix_sql'] if best_case and best_case.get("fix_sql") else None
                    suggestion = prompt_gemini_with_error(schema_text, sql_query, error_msg, english_query, best_case)
                    print("💡 Gemini suggests:\n", suggestion)
                    # Attempt to run suggested SQL
                    try:
                        fix_result = execute_sql_tool(db_url, suggestion)
                        print("Fixed Answer:\n", fix_result)
                        # Store new working pattern!
                        store_error_pattern(schema_text, sql_query, error_msg, english_query, suggestion)
                    except Exception as inner_e:
                        print("Even after fix, error:", inner_e)
            else:
                print("No SQL code detected in agent output.")
        except Exception as e:
            print("\n[ERROR]:", str(e), "\n")
