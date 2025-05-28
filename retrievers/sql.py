import duckdb

def run_sql_query(query):
    conn = None 
    try:
        conn = duckdb.connect(database=':memory:', read_only=False)
        csv_path = 'data/energy_bids.csv'
        conn.execute(f"CREATE OR REPLACE VIEW energy_bids_data AS SELECT * FROM '{csv_path}'")
        adapted_query = query.replace('energy_bids_file', 'energy_bids_data').replace('requests', 'energy_bids_data').replace('requests_table', 'energy_bids_data')
        result = conn.execute(adapted_query).df()
        return result.to_string(index=False)
    except Exception as e:
        return f"SQL Error: {e}"
    finally:
        if conn:
            conn.close()
