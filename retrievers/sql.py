import duckdb

def run_sql_query(query):
    try:
        result = duckdb.sql(query).df()
        return result.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {e}"
