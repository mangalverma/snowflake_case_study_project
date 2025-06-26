import streamlit as st
from utils.helpers import deep_equal
import os
from glob import glob
import json

def load_configurations(table_view):
    warehouse = st.secrets["snowflake"]["warehouse"]
    database = st.secrets["snowflake"]["database"]

    wh_dir = os.path.join("config_file",warehouse)
    if not os.path.exists(wh_dir):
        os.mkdir(wh_dir)
    db_dir = os.path.join(wh_dir,database)
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    table_dir = os.path.join(db_dir,table_view)
    if not os.path.exists(table_dir):
        os.mkdir(table_dir)

    configs = dict()
    for config_file in glob(table_dir+"/*"):
        with open(config_file) as f:
            jd = json.loads(f.read())
        configs[jd['name']] = jd
    return configs


def save_configuration(table_view,config_data,input_config_data):
    warehouse = st.secrets["snowflake"]["warehouse"]
    database = st.secrets["snowflake"]["database"]

    wh_dir = os.path.join("config_file", warehouse)
    if not os.path.exists(wh_dir):
        os.mkdir(wh_dir)
    db_dir = os.path.join(wh_dir, database)
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)

    table_dir = os.path.join(db_dir, table_view)
    if not os.path.exists(table_dir):
        os.mkdir(table_dir)

    is_new_config_data = deep_equal(config_data,input_config_data)
    print("is_new_config_data :",str(is_new_config_data))
    if is_new_config_data:
        version_num = 0
        version_str = config_data['name'].split("_")[-1]
        if version_str.startswith("v"):
            version_num = version_str.replace("v","")
            try:
                version_num = int(version_num)
            except Exception as e:
                print(e)
            version_num+=1
            view_name = "_".join(config_data['name'].split("_")[:-1])+f"_v{version_num}"
        else:
            view_name = f"{config_data['name']}_v0"
        config_data['name'] = view_name
        config_filename = view_name + ".json"
        config_file_path = os.path.join(table_dir,config_filename)
        with open(config_file_path,'w+') as f:
            f.write(json.dumps(config_data))
        return  {'config_filename':config_filename,"view_name":view_name,'message':"NEW_FILE_CREATED"}
    else:
        return {"message":"SAME_FILE_CREATED"}

def prepare_config_file(rules,filters,config_name):
    new_filters = []
    for f in filters:
        if "added_by_config" in f:
            del f["added_by_config"]
        new_filters.append(f)
    config_data = {
        'name':config_name,
        'rules':rules,
        'filters':new_filters
    }
    return config_data



