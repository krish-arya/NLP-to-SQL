from sqlalchemy import create_engine, inspect

def extract_schema(connection_string):
    """
    Returns a list of table schemas with foreign keys.
    """
    engine = create_engine(connection_string)
    inspector = inspect(engine)

    schema = []
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        column_info = [
            f"{col['name']} {str(col['type'])}" for col in columns
        ]

        fks = inspector.get_foreign_keys(table_name)
        foreign_keys = [
            f"{fk['constrained_columns']} REFERENCES {fk['referred_table']}" for fk in fks
        ]

        schema.append({
            "table": table_name,
            "columns": column_info,
            "foreign_keys": foreign_keys
        })

    return schema

def render_schema_text(schema):
    lines = []
    for table in schema:
        lines.append(f"Table: {table['table']}")
        lines.extend([f"- {col}" for col in table['columns']])
        if table['foreign_keys']:
            lines.extend([f"  FOREIGN KEY: {fk}" for fk in table['foreign_keys']])
        lines.append("")
    return "\n".join(lines)
