import streamlit as st
from data_source.metadata_extractor import get_columns
from data_source.snowflake_connector import get_connection,execute_sql,create_snowflake_view
from data_source.metadata_extractor import get_tables_and_views, get_columns,fetch_preview_source_data
from config.config_manager import load_configurations
# from ui_components.source_selector import render_source_selector
from ui_components.filter_builder import render_filter_section
from ui_components.rule_builder import render_rule_section
from utils.sql_generator import generate_sql

# Page Setup
st.set_page_config(page_title="Extraction Configurator", layout="wide")
st.title(" Extraction Framework Configurator")

# Session state initialization
if 'selected_source' not in st.session_state:
    st.session_state.selected_source = None


conn = get_connection()
# --- Source Selection ---
st.header("Select Data Source")

available_sources = get_tables_and_views(conn)
selected_source = st.selectbox(f"Select Source Name", available_sources)
st.session_state.selected_source = selected_source

if st.button("Run and Preview Source Data"):
    try:
        preview_df = fetch_preview_source_data(selected_source)
        st.markdown("### Data Preview")
        st.dataframe(preview_df)
    except Exception as e:
        st.error(f"Failed to run preview: {e}")


config_details = load_configurations(selected_source)
selected_config = st.selectbox("Choose configuration or create new:", list(config_details.keys()) + ["➕ Create New"])
is_config_exist = 0 if selected_config == "➕ Create New" else 1
new_created_config = st.text_input("Enter New Configuration name", disabled=is_config_exist)

if (selected_config=="➕ Create New") and (new_created_config!=""):
    selected_config = new_created_config

# --- Filter Builder UI ---
st.header("Global Extract Filters")
if is_config_exist and selected_config:
    if "selected_config" not in st.session_state:
        st.session_state.selected_config = {'name':selected_config,'filters': config_details[selected_config].get('filters', []),'filter_loaded':False}
    else:
        if st.session_state.selected_config['name']!=selected_config:
            st.session_state.selected_config = {'name': selected_config,
                                                'filters': config_details[selected_config].get('filters', []),
                                                'filter_loaded': False}

else:
    st.session_state.selected_config = {'name':selected_config,'filters': [],'filter_loaded':False}
# print(st.session_state)


# print("selected_config",selected_config)
filters = render_filter_section(conn, selected_source, selected_config)
# print("Filters")
# print(filters)

# --- Rule Engine Section ---
st.header("Attribute Rules (CASE-WHEN)")
rules = render_rule_section(conn,selected_source,config_name=selected_config,
                            simple_config=config_details[selected_config]["rules"].get("simple_rules", []),
                            complex_config=config_details[selected_config]["rules"].get("complex_rules", []))
# print("Rules")
# print(rules)

sql = generate_sql(selected_source, get_columns(conn, selected_source), filters, rules)
# --- SQL Preview ---
if st.button("Preview SQL Results"):
    st.markdown("### Latest Generated SQL")
    st.code(sql, language='sql')
    sql_preview_result_df = execute_sql(sql)
    st.markdown("### Latest SQL Preview")
    st.dataframe(sql_preview_result_df)

# --- Save Configuration ---
if st.button("Save Configuration"):
    from config.config_manager import save_configuration,prepare_config_file
    config_data = prepare_config_file(rules, filters,selected_config)
    response = save_configuration(table_view=selected_source,config_data=config_data,input_config_data=config_details.get(selected_config,{}))
    if response['message']=="NEW_FILE_CREATED":
        config_filename = response['config_filename']
        st.success(f"Configuration file {config_filename} saved successfully!")
        view_name = response['view_name']
        view_response = create_snowflake_view(view_name=view_name,sql_query=sql,conn=conn)
        if view_response:
            st.success(f"""view "{view_name}" created successfully!""")
        else:
            st.error(f"""view "{view_name}" not created! something went wrong """)
    elif response['message']=="SAME_FILE_CREATED":
        st.success(f"""No Modification done by user !! so no view and config file create""")
    else:
        st.error(f"""NO FILE CREATED SOMETHING WENT WRONG!!""")



