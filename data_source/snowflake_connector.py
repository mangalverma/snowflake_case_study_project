import snowflake.connector
import pandas as pd
import streamlit as st
import os

def get_connection():
    """
    Establishes and returns a Snowflake connection using Streamlit secrets.
    """
    if "snowflake_conn" not in st.session_state:
        try:
            conn = snowflake.connector.connect(
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            account=st.secrets["snowflake"]["account"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            )
            st.session_state.snowflake_conn = conn
            return conn
        except Exception as e:
            print(e)
            st.error("❌ Error connecting to Snowflake.")
            st.stop()
    else:
        return st.session_state.snowflake_conn

def execute_sql(sql):
    conn = get_connection()
    df = pd.read_sql(sql, conn)
    return df



def create_snowflake_view(view_name, sql_query, conn):
    try:
        cursor = conn.cursor()
        create_view_sql = f"CREATE OR REPLACE VIEW {view_name} AS {sql_query}"
        cursor.execute(create_view_sql)
        success = True
    except Exception as e:
        print(e)
        success = False
    return success

