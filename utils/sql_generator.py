import streamlit as st

def generate_sql(base_table: str, selected_columns: list, filters: list, rules: list) -> str:
    """
    Generate SQL SELECT statement using given columns, filters, and CASE WHEN rules.
    """
    select_clauses = []
    # Base columns
    if selected_columns:
        select_clauses.extend(selected_columns)
    else:
        select_clauses.append("*")

    # Add rule-based columns
    for rule in rules['simple_rules']:
            case_expr = f"CASE WHEN {rule['column']} {rule['operator']} '{rule['value']}' THEN '{rule['then']}' ELSE '{rule['else']}' END AS {rule['alias']}"
            select_clauses.append(case_expr)
    for rule in rules['complex_rules']:
            whens = " ".join([
                f"WHEN {cond['column']} {cond['operator']} '{cond['value']}' THEN '{cond['then']}'"
                for cond in rule["conditions"]
            ])
            case_expr = f"CASE {whens} ELSE '{rule['else']}' END AS {rule['alias']}"
            select_clauses.append(case_expr)

    select_stmt = f"SELECT {', '.join(select_clauses)} FROM {base_table}"

    # Apply filters
    where_clauses = []
    for f in filters:
        if f["type"] == "WHERE":
            condition = f"{f['column']} {f['condition']} '{f['value']}'"
            where_clauses.append(condition)
        elif f["type"] == "IN":
            in_vals = ", ".join([f"'{v}'" for v in f["values"]])
            where_clauses.append(f"{f['column']} IN ({in_vals})")
        elif f["type"] == "BETWEEN":
            where_clauses.append(f"{f['column']} BETWEEN '{f['from']}' AND '{f['to']}'")

    if where_clauses:
        select_stmt += " WHERE " + " AND ".join(where_clauses)

    return select_stmt

# def render_preview_button(conn, table_name: str, selected_columns: list, filters: list, rules: list):
#     st.markdown("### 🔍 Preview SQL Results")
#     if st.button("💡 Preview SQL"):
#         query = generate_sql(table_name, selected_columns, filters, rules)
#         st.code(query, language="sql")
#         try:
#             df = conn.cursor().execute(query).fetch_pandas_all()
#             st.dataframe(df)
#         except Exception as e:
#             st.error(f"Failed to execute query: {e}")
