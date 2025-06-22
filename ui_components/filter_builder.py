import streamlit as st
from data_source.metadata_extractor import get_columns


def render_filter_section(conn, table_name, selected_config):
    if "filters" not in st.session_state:
        st.session_state.filters = []

    if selected_config == st.session_state.selected_config['name']:
        if st.session_state.selected_config['filter_loaded'] == False:
            st.session_state.filters = [filt for filt in st.session_state.filters if 'added_by_config' not in filt]
            for filt in st.session_state.selected_config['filters']:
                filt['added_by_config'] = True
                st.session_state.filters.append(filt)
            st.session_state.selected_config['filter_loaded'] = True

    if table_name:
        columns = get_columns(conn, table_name)
    else:
        columns = []

    filter_type_options = ["WHERE", "IN", "BETWEEN"]
    condition_options = ["=", "!=", "<", ">", "<=", ">=", "LIKE"]

    def add_filter():
        st.session_state.filters.append({
            "type": "WHERE",
            "column": columns[0] if columns else "",
            "condition": "=",
            "value": "",
            "values": [],
            "from": "",
            "to": "",
            "case_sensitive": False,
            "combine_with_next": "AND",
            "applied": False
        })

    st.button("➕ Add Filter", on_click=add_filter)

    filters_to_return = []

    for i, filter in enumerate(st.session_state.filters):
        with st.expander(f"Filter #{i + 1}", expanded=True):
            filter_type = st.selectbox("Filter Type", filter_type_options,
                                       index = filter_type_options.index(filter["type"]) if filter["type"] in filter_type_options else 0,
                                       key=f"filter_type_{i}")
            filter_data = {"type": filter_type}

            if filter_type == "WHERE":
                cols1, cols2, cols3 = st.columns(3)
                column = cols1.selectbox("Column", columns,
                                         index=columns.index(filter["column"]) if filter["column"] in columns else 0,
                                         key=f"column_{i}")
                condition = cols2.selectbox("Condition", condition_options,index=condition_options.index(filter["condition"]) if filter["condition"] in condition_options else 0, key=f"condition_{i}")
                value = cols3.text_input("Value", value = filter.get('value',''),key=f"value_{i}")
                filter_data.update({"condition": condition, "value": value, "column": column})

            elif filter_type == "IN":
                cols1, cols2 = st.columns(2)
                column = cols1.selectbox("Column", columns,
                                         index=columns.index(filter["column"]) if filter["column"] in columns else 0,
                                         key=f"column_{i}")
                value = cols2.text_area("Comma-separated values", key=f"in_values_{i}",value=",".join(filter['values']))
                values = [v.strip() for v in value.split(",") if v.strip()]
                filter_data.update({"values": values, "column": column})

            elif filter_type == "BETWEEN":
                cols1, cols2, cols3 = st.columns(3)
                column = cols1.selectbox("Column", columns,
                                         index=columns.index(filter["column"]) if filter["column"] in columns else 0,
                                         key=f"column_{i}")
                from_val = cols2.text_input("From", key=f"from_{i}",value = filter.get("from",""))
                to_val = cols3.text_input("To", key=f"to_{i}",value = filter.get("to",""))
                filter_data.update({"from": from_val, "to": to_val, "column": column})

            case_sensitive = st.checkbox("Case Sensitive? (only for text)",
                                         value=filter.get("case_sensitive", False),
                                         key=f"case_sensitive_{i}")
            combine = st.selectbox("Combine with next using", ["AND", "OR"],index = ["AND", "OR"].index(filter["combine_with_next"]) if filter["combine_with_next"] in ["AND", "OR"] else 0, key=f"combine_{i}")

            filter_data.update({
                "case_sensitive": case_sensitive,
                "combine_with_next": combine
            })

            cols_btn1, cols_btn2 = st.columns(2)

            with cols_btn1:
                if st.button("✅ Apply Filter", key=f"apply_{i}"):
                    filter_data["applied"] = True
                    st.session_state.filters[i] = filter_data
                    st.success(f"Filter #{i + 1} applied")

            with cols_btn2:
                if st.button("❌ Cancel Filter", key=f"cancel_{i}"):
                    st.session_state.filters.pop(i)
                    st.rerun()

            # Only return applied filters
            if filter.get("applied", False):
                filters_to_return.append(filter)
    return filters_to_return

