import json, mysql.connector, sys

try:
    mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)
except Exception as e:
    print(e)

mycursor = mydb.cursor()

# Create database
mycursor.execute("CREATE DATABASE IF NOT EXISTS bikes")
mycursor.execute("USE bikes")


ALL_BIKES_DATA = {}

# Open json_dile and load the data into python dictionary
with open("all_bikes_data.json", "r") as json_file:
    json_data = json_file.read()
    ALL_BIKES_DATA = json.loads(json_data)


def delete_all_tables():
    mycursor.execute("DROP DATABASE IF EXISTS bikes")
    mycursor.execute("CREATE DATABASE IF NOT EXISTS bikes")
    mycursor.execute("USE bikes")


def create_index_table():
    table = "index_table"
    col_names = "model_name VARCHAR(255), table_name VARCHAR(255)"
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_names})")
    mydb.commit()
    for k, v in ALL_BIKES_DATA.items():
        for k, v in v.items():
            model_name = k.lower()
            sql = f"INSERT INTO {table} (model_name) VALUES(%s)"
            val = (model_name,)
            mycursor.execute(sql, val)
            mydb.commit()


def get_types_list():
    types_list = []
    for val in ALL_BIKES_DATA.values():
        for v in val.values():
            for k, v in v.items():
                if k == "body_type":
                    v = v.replace(",", "").lower()
                    types_list.append(v.replace(" ", "_"))
    types_list = sorted(set(types_list))
    return types_list


def create_types_table():
    types_list = get_types_list()
    table = "types_table"
    col_names = "type_names VARCHAR(255)"
    print(f"Creating table {table}")
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_names})")
    mydb.commit()
    for name in types_list:
        sql = f"INSERT INTO {table} (type_names) VALUES(%s)"
        val = (name,)
        mycursor.execute(sql, val)
        mydb.commit()
    return types_list


def create_brands_table():
    dct = {}
    with open("brand_logos.json", "r") as json_file:
        dct = json.loads(json_file.read())
    table = "brands_table"
    col_names = "brand_names VARCHAR(255), brand_logos VARCHAR(255)"
    print(f"Creating table {table}")
    mycursor.execute(f"CREATE TABLE IF NOT EXISTS {table} ({col_names})")
    mydb.commit()
    for name, logo in dct.items():
        name = name.replace("-", "_").lower()
        name = name[:-6]
        sql = f"INSERT INTO {table} (brand_names, brand_logos) VALUES(%s, %s)"
        val = (name, logo,)
        mycursor.execute(sql, val)
        mydb.commit()


def update_database():
    # Delete all existing tables first
    delete_all_tables()

    # Create basic tables first
    create_index_table()
    create_brands_table()
    types_list = create_types_table()

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

    # Create type_based tables
    print("Creating type_based bike spec tables")
    for typ in types_list:
        print(f"\tCreating table {typ}")
        mycursor.execute(f"CREATE TABLE IF NOT EXISTS {typ} ({col_names})")
        mydb.commit()
        for val in ALL_BIKES_DATA.values():
            for k, v in val.items():
                model_name = k.lower()
                if "body_type" in v.keys():
                    body_type = v["body_type"]
                    body_type = body_type.replace(",", "")
                    body_type = body_type.replace(" ", "_").lower()
                    if body_type == typ:
                        print(f"\tInserting data into {typ} table")
                        sql = f"INSERT INTO {typ} (model_name) VALUES (%s)"
                        val = (model_name,)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        for k, v in v.items():
                            print(f"\t\tUpdating {k} data of {model_name} in {typ} table")
                            sql = f"UPDATE {typ} SET {k}='{v}' WHERE model_name=%s"
                            val = (model_name,)
                            mycursor.execute(sql, val)
                            mydb.commit()


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
            print(f"\t\tInserting index_table entry for easy retrieval of data")
            sql = f"UPDATE index_table SET table_name='{table}' WHERE model_name=%s"
            val = (model_name,)
            mycursor.execute(sql, val)
            mydb.commit()


update_database()
