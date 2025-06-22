from data_source.snowflake_connector import execute_sql

def get_tables_and_views(conn):
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[1] for row in cursor.fetchall()]
    cursor.execute("SHOW VIEWS")
    views = [row[1] for row in cursor.fetchall()]
    return tables + views

def fetch_preview_source_data(selected_source):
        sql = f"SELECT * FROM {selected_source} LIMIT 100"
        preview_df = execute_sql(sql)
        return preview_df

def get_columns(conn,table):
    cursor = conn.cursor()
    cursor.execute(f"DESC TABLE {table}")
    columns = [row[0] for row in cursor.fetchall()]
    return columns