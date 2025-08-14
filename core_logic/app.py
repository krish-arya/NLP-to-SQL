# app.py
import os
import re
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# your modules (same names as in your script)
from schema_extractor import extract_schema, render_schema_text
from vector_store import create_schema_store, query_schema_store
from agent_runner import build_agent
from llm_language_router import route_query
from self_healing_vector_db import store_error_pattern, search_similar_errors, prompt_gemini_with_error
from tools import execute_sql_tool  # your existing executor; fallback below if missing

# Optional helper: use sqlalchemy fallback if execute_sql_tool is not available
def sqlalchemy_execute(db_url, query):
    from sqlalchemy import create_engine, text
    engine = create_engine(db_url, connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {})
    with engine.connect() as conn:
        res = conn.execute(text(query))
        rows = [dict(r) for r in res]
    return rows

# simple safety check (use sqlparse for robust parsing)
def is_safe_select(sql_text: str) -> bool:
    s = sql_text.strip().lower()
    # quick guard: allow only statements that start with SELECT
    return s.startswith("select")

# globals to hold heavy objects
initialized = False
schema_text = ""
collection = None
agent = None
chunks = []

CONNECTION_STRING = os.getenv("DATABASE_URL", "sqlite:///example.db")

def create_app():
    app = Flask(__name__)
    CORS(app)
    logging.basicConfig(level=logging.INFO)

    @app.before_request
    def startup():
        global initialized, schema_text, collection, agent, chunks
        if initialized:
            return
        app.logger.info("Initializing schema and agent...")
        schema = extract_schema(CONNECTION_STRING)
        schema_text = render_schema_text(schema)
        chunks = schema_text.split("\n\n")
        collection = create_schema_store(chunks)
        agent = build_agent()
        initialized = True
        app.logger.info("Initialization complete.")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/chat", methods=["POST"])
    def chat():
        try:
            data = request.get_json(force=True)
            question = data.get("question") or ""
            if not question:
                return jsonify({"error": "missing 'question' field"}), 400

            english_query = route_query(question)
            top_chunks = query_schema_store(collection, english_query)
            schema_context = "\n".join(top_chunks)

            full_input = f"{english_query}\n\nSCHEMA CONTEXT:\n{schema_context}"

            # call agent
            response = agent.invoke({"input": full_input})
            agent_output = response['output'] if isinstance(response, dict) and 'output' in response else response

            # try to capture SQL fenced in triple backticks (```sql ... ```)
            sql_match = re.search(r"```(?:sql)?\s*(.*?)```", str(agent_output), re.DOTALL | re.IGNORECASE)
            sql_query = sql_match.group(1).strip() if sql_match else None

            result_rows = None
            error_msg = None
            gemini_suggestion = None
            fix_result = None

            if sql_query:
                # safety check
                if not is_safe_select(sql_query):
                    return jsonify({
                        "agent_output": agent_output,
                        "sql": sql_query,
                        "executed": False,
                        "reason": "Only SELECT queries are allowed to be executed automatically."
                    }), 200

                db_url = os.getenv("DATABASE_URL", CONNECTION_STRING)
                try:
                    # try your execute_sql_tool first; otherwise fallback
                    try:
                        result_rows = execute_sql_tool(db_url, sql_query)
                    except NameError:
                        result_rows = sqlalchemy_execute(db_url, sql_query)
                except Exception as e:
                    error_msg = str(e)
                    # self-healing flow
                    sim_errors = search_similar_errors(schema_text, sql_query, error_msg, english_query)
                    best_case = sim_errors[0]['meta'] if sim_errors else None
                    gemini_suggestion = prompt_gemini_with_error(schema_text, sql_query, error_msg, english_query, best_case)
                    # attempt suggested fix only if safe
                    if gemini_suggestion and is_safe_select(gemini_suggestion):
                        try:
                            try:
                                fix_result = execute_sql_tool(db_url, gemini_suggestion)
                            except NameError:
                                fix_result = sqlalchemy_execute(db_url, gemini_suggestion)
                            # store pattern so future errors can be fixed automatically
                            store_error_pattern(schema_text, sql_query, error_msg, english_query, gemini_suggestion)
                        except Exception as inner_e:
                            # keep both errors
                            error_msg = f"{error_msg}; fix_attempt_error: {inner_e}"

            return jsonify({
                "agent_output": agent_output,
                "sql": sql_query,
                "rows": result_rows,
                "error": error_msg,
                "gemini_suggestion": gemini_suggestion,
                "fix_result": fix_result
            }), 200
        except Exception as e:
            app.logger.exception("Unhandled error in /chat")
            return jsonify({"error": "internal_server_error", "detail": str(e)}), 500

    # optional: endpoint to reload schema (admin only — add auth in prod)
    @app.route("/reload-schema", methods=["POST"])
    def reload_schema():
        global schema_text, collection, agent, chunks
        schema = extract_schema(CONNECTION_STRING)
        schema_text = render_schema_text(schema)
        chunks = schema_text.split("\n\n")
        collection = create_schema_store(chunks)
        return jsonify({"status": "schema reloaded"}), 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
