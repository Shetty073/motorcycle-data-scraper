import json, mysql.connector, sys

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

mycursor = mydb.cursor()

# Create database
mycursor.execute("CREATE DATABASE IF NOT EXISTS bikes")
mycursor.execute("USE bikes")


ALL_BIKES_DATA = {}

def load_json():
    # Open json_dile and load the data into python dictionary
    with open("all_bikes_data.json", "r") as json_file:
        json_data = json_file.read()
        ALL_BIKES_DATA = json.loads(json_data)


def delete_all_tables():
    for brand in ALL_BIKES_DATA.keys():
        print(f"Dropping tables {brand}")
        mycursor.execute(F"DROP TABLES IF EXISTS {brand}")


def update_database():
    # Load data from 'all_bikes-data.json' into dictionary
    load_json()

    # Delete all existing tables first
    delete_all_tables()

    # Prepare columns list
    values_list = []
    for k, v in ALL_BIKES_DATA.items():
        for key, value in v.items():
            for k, v in value.items():
                values_list.append(k)
            
    old_col_names = sorted(set(values_list))
    col_names = "model_name VARCHAR(255), "
    for x in old_col_names:
        temp = (x + " VARCHAR(255), ")
        col_names += temp
    col_names = col_names[:-2]

    # Create tables and insert data
    for k, v in ALL_BIKES_DATA.items():
        table = k
        mycursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_names})")
        for k, v in v.items():
            model_name = k.lower()
            print(f"\tInserting {k} data into {table} table")
            sql = f"INSERT INTO {table} (model_name) VALUES (%s)"
            val = (model_name,)
            mycursor.execute(sql, val)
            mydb.commit()
            for key, value in v.items():
                print(f"\t\tUpdating {key} data of {model_name}")
                sql = f"UPDATE {table} SET {key}='{value}' WHERE model_name=%s"
                val = (model_name,)
                mycursor.execute(sql, val)
                mydb.commit()


update_database()
