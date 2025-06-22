import streamlit as st
from data_source.metadata_extractor import get_columns

def render_rule_section(conn, table, config_name, simple_config=[], complex_config=[]):

    all_columns = get_columns(conn,table)

    if "simple_rules" not in st.session_state:
        st.session_state.simple_rules = []
    if "complex_rules" not in st.session_state:
        st.session_state.complex_rules = []
    if "complex_conditions" not in st.session_state:
        st.session_state.complex_conditions = []
    if "rule_mode" not in st.session_state:
        st.session_state.rule_mode = None
    if "edit_rule" not in st.session_state:
        st.session_state.edit_rule = None

    def reset_edit():
        st.session_state.edit_rule = None

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Simple Rule"):
            st.session_state.rule_mode = "simple"
            reset_edit()
    with col2:
        if st.button("Complex Rule"):
            st.session_state.rule_mode = "complex"
            reset_edit()

    config_rules = []
    rule_options = config_rules if config_rules else ["None"]

    if st.session_state.rule_mode == "simple":
        simple_rule_names = [r["name"] for r in simple_config]
        selected_simple = st.selectbox("Load Existing Rule", ["None"] + simple_rule_names, key="load_simple")

        if selected_simple != "None":
            selected_rule = next((r for r in simple_config if r["name"] == selected_simple), None)
            if selected_rule:
                st.session_state.edit_rule = selected_rule.copy()
                st.session_state.rule_mode = "simple"

        if st.session_state.edit_rule and st.session_state.edit_rule["type"] == "simple":
            rule_data = st.session_state.edit_rule
        else:
            rule_data = {"name": "", "description": "", "column": "", "operator": "=", "value": "", "then": "", "else": "", "alias": ""}

        rule_name = st.text_input("Rule Name", value=rule_data["name"], key="simple_name")
        rule_desc = st.text_input("Rule Description", value=rule_data["description"], key="simple_desc")

        col1, col2, col3 = st.columns([3, 2, 3])
        with col1:
            column = st.selectbox("Column", all_columns or ["No columns"], index=(all_columns.index(rule_data["column"]) if rule_data["column"] in all_columns else 0), key="simple_col")
        with col2:
            operator = st.selectbox("Condition", ["=", "!=", "<", ">", "<=", ">=", "LIKE"], index=["=", "!=", "<", ">", "<=", ">=", "LIKE"].index(rule_data["operator"] if rule_data["operator"] in ["=", "!=", "<", ">", "<=", ">=", "LIKE"] else "="), key="simple_op")
        with col3:
            value = st.text_input("Value", value=rule_data["value"], key="simple_val")

        then = st.text_input("THEN", value=rule_data["then"], key="simple_then")
        else_val = st.text_input("ELSE", value=rule_data["else"], key="simple_else")
        alias = st.text_input("NEW_COLUMN (Alias)", value=rule_data["alias"], key="simple_alias")

        if st.button("➕ Apply Simple Rule"):
            rule = {
                "type": "simple",
                "name": rule_name,
                "description": rule_desc,
                "column": column,
                "operator": operator,
                "value": value,
                "then": then,
                "else": else_val,
                "alias": alias
            }
            st.session_state.simple_rules.append(rule)
            reset_edit()
            st.success(f"Simple Rule '{rule_name}' added.")

    elif st.session_state.rule_mode == "complex":
        complex_rule_names = [r["name"] for r in complex_config]
        selected_complex = st.selectbox("Load Existing Rule", ["None"] + complex_rule_names, key="load_complex")
        if selected_complex != "None":
            selected_rule = next((r for r in complex_config if r["name"] == selected_complex), None)
            if selected_rule:
                st.session_state.edit_rule = selected_rule.copy()
                st.session_state.edit_complex_conditions = selected_rule.get("conditions", []).copy()
                st.session_state.rule_mode = "complex"

        if st.session_state.edit_rule and st.session_state.edit_rule["type"] == "complex":
            rule_data = st.session_state.edit_rule
        else:
            rule_data = {"name": "", "description": "", "conditions": [], "else": "", "alias": ""}

        rule_name = st.text_input("Rule Name", value=rule_data["name"], key="complex_name")
        rule_desc = st.text_input("Rule Description", value=rule_data["description"], key="complex_desc")

        if "edit_complex_conditions" not in st.session_state:
            st.session_state.edit_complex_conditions = rule_data["conditions"] or []

        st.markdown("#### WHEN Conditions")
        for i, cond in enumerate(st.session_state.edit_complex_conditions):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                cond["column"] = st.selectbox(f"Column {i+1}", all_columns or [""], index=(all_columns.index(cond["column"]) if cond["column"] in all_columns else 0), key=f"c_col_edit_{i}")
            with c2:
                cond["operator"] = st.selectbox(f"Operator {i+1}", ["=", "!=", "<", ">", "<=", ">=", "LIKE"], index=["=", "!=", "<", ">", "<=", ">=", "LIKE"].index(cond["operator"] if cond["operator"] in ["=", "!=", "<", ">", "<=", ">=", "LIKE"] else "="), key=f"c_op_edit_{i}")
            with c3:
                cond["value"] = st.text_input(f"Value {i+1}", value=cond["value"], key=f"c_val_edit_{i}")
            with c4:
                cond["then"] = st.text_input(f"THEN {i+1}", value=cond["then"], key=f"c_then_edit_{i}")

        if st.button("ADD CONDITION"):
            st.session_state.edit_complex_conditions.append({"column": all_columns[0] if all_columns else "", "operator": "=", "value": "", "then": ""})
            st.rerun()

        else_val = st.text_input("ELSE", value=rule_data["else"], key="complex_else")
        alias = st.text_input("NEW_COLUMN (Alias)", value=rule_data["alias"], key="complex_alias")

        if st.button("➕ Apply Complex Rule"):
            rule = {
                "type": "complex",
                "name": rule_name,
                "description": rule_desc,
                "conditions": st.session_state.edit_complex_conditions,
                "else": else_val,
                "alias": alias
            }
            st.session_state.complex_rules.append(rule)
            st.session_state.edit_complex_conditions = []
            reset_edit()
            st.success(f"Complex Rule '{rule_name}' added.")

    st.markdown("### Current Rules")
    for i, rule in enumerate(st.session_state.simple_rules):
        with st.expander(f"Simple Rule {i+1}: {rule['name']}"):
            colA, colB, colC = st.columns(3)
            with colA:
                if st.button(f"✅ Edit {i+1}", key=f"edit_simple_{i}"):
                    st.session_state.edit_rule = rule
                    st.session_state.simple_rules.pop(i)
                    st.session_state.rule_mode = "simple"
                    st.rerun()
            with colB:
                if st.button(f"❌ Cancel {i+1}", key=f"cancel_simple_{i}"):
                    st.session_state.simple_rules.pop(i)
                    st.rerun()

    for j, rule in enumerate(st.session_state.complex_rules):
        with st.expander(f"Complex Rule {j+1}: {rule['name']}"):
            colD, colE, colF = st.columns(3)
            with colD:
                if st.button(f"Edit {j+1}", key=f"edit_complex_{j}"):
                    st.session_state.edit_rule = rule
                    st.session_state.complex_rules.pop(j)
                    st.session_state.edit_complex_conditions = rule["conditions"]
                    st.session_state.rule_mode = "complex"
                    st.rerun()
            with colE:
                if st.button(f"Cancel {j+1}", key=f"cancel_complex_{j}"):
                    st.session_state.complex_rules.pop(j)
                    st.rerun()
    return {"simple_rules":st.session_state.simple_rules,"complex_rules":st.session_state.complex_rules}