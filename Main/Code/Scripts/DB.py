import psycopg2
import csv
import re
from dotenv import load_dotenv
import os


# Creation Queries for the tables
Tunisianet_Pc_Portable_Gamer = ["Tunisianet_Pc_Portable_Gamer", """CREATE TABLE IF NOT EXISTS Tunisianet_Pc_Portable_Gamer (
title text,
price integer,
link TEXT PRIMARY KEY ,
image text,
availability text,
site_id  text,
brand text,
model text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint,
wifi smallint,
bluetooth smallint,
keyboard text,
screen_type text,
screen_size real,
screen_resolution text,
screen_refresh_rate integer
)
"""]

Mytek_Pc_Portable_Gamer = ["Mytek_Pc_Portable_Gamer","""CREATE TABLE IF NOT EXISTS Mytek_Pc_Portable_Gamer (
title text,
price integer,
link text PRIMARY KEY,
image text,
availability text,
site_id  text,
brand text,
model text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint,
wifi smallint,
bluetooth smallint,
keyboard text,
screen_type text,
screen_size real,
screen_resolution text,
screen_refresh_rate integer
)
"""]

ScoopGaming_Pc_Portable_Gamer = ["ScoopGaming_Pc_Portable_Gamer","""CREATE TABLE IF NOT EXISTS ScoopGaming_Pc_Portable_Gamer (
title text,
price integer,
link text PRIMARY KEY,
image text,
availability text,
site_id  text,
brand text,
model text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint,
wifi smallint,
bluetooth smallint,
keyboard text,
screen_type text,
screen_size real,
screen_resolution text,
screen_refresh_rate integer
)
"""]

Tunisianet_Pc_Bureau_Gamer = ["Tunisianet_Pc_Bureau_Gamer", """CREATE TABLE IF NOT EXISTS Tunisianet_Pc_Bureau_Gamer (
title text,
price integer,
link text PRIMARY KEY,
image text,
availability text,
site_id  text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint
)
"""]

Mytek_Pc_Bureau_Gamer = ["Mytek_Pc_Bureau_Gamer", """CREATE TABLE IF NOT EXISTS Mytek_Pc_Bureau_Gamer (
title text,
price integer,
link text PRIMARY KEY,
image text,
availability text,
site_id  text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint
)
"""]

ScoopGaming_Pc_Bureau_Gamer = ["ScoopGaming_Pc_Bureau_Gamer", """CREATE TABLE IF NOT EXISTS ScoopGaming_Pc_Bureau_Gamer (
title text,
price integer,
link text PRIMARY KEY,
image text,
availability text,
site_id  text,
cpu_brand text,
cpu_model text,
cpu_cores smallint,
cpu_frequency real,
ram_size smallint,
ram_type text,
storage_size smallint,
storage_type text,
gpu_brand text,
gpu_model text,
gpu_memory smallint
)
"""]

Tunisianet_Ecran_Gamer = ["Tunisianet_Ecran_Gamer","""CREATE TABLE IF NOT EXISTS Tunisianet_Ecran_Gamer (
title text,
price integer,
link TEXT PRIMARY KEY,
image text,
availability text,
site_id  text,
brand text,
panel_type text,
size real,
resolution text,
refresh_rate integer,
response_time smallint,
contrast text,
brightness smallint,
viewing_angle text,
curvature smallint,
audio_ports boolean,
flicker_free boolean,
blue_light_filter boolean,
adaptive_sync boolean
)
"""]

Mytek_Ecran_Gamer = ["Mytek_Ecran_Gamer","""CREATE TABLE IF NOT EXISTS Mytek_Ecran_Gamer (
title text,
price integer,
link TEXT PRIMARY KEY,
image text,
availability text,
site_id  text,
brand text,
panel_type text,
size real,
resolution text,
refresh_rate integer,
response_time smallint,
contrast text,
brightness smallint,
viewing_angle text,
curvature smallint,
audio_ports boolean,
flicker_free boolean,
blue_light_filter boolean,
adaptive_sync boolean
)
"""]

ScoopGaming_Ecran_Gamer = ["ScoopGaming_Ecran_Gamer","""CREATE TABLE IF NOT EXISTS ScoopGaming_Ecran_Gamer (
title text,
price integer,
link TEXT PRIMARY KEY,
image text,
availability text,
site_id  text,
brand text,
panel_type text,
size real,
resolution text,
refresh_rate integer,
response_time smallint,
contrast text,
brightness smallint,
viewing_angle text,
curvature smallint,
audio_ports boolean,
flicker_free boolean,
blue_light_filter boolean,
adaptive_sync boolean
)
"""]

Table_Queries = [Tunisianet_Pc_Portable_Gamer,Mytek_Pc_Portable_Gamer, ScoopGaming_Pc_Portable_Gamer, Tunisianet_Pc_Bureau_Gamer, Mytek_Pc_Bureau_Gamer, ScoopGaming_Pc_Bureau_Gamer, Tunisianet_Ecran_Gamer, Mytek_Ecran_Gamer, ScoopGaming_Ecran_Gamer]

def Create_Table(cursor, query):
    # Create a table in the database
    try:
        cursor.execute(query[1])
        print("Created Table " + query[0])
    except Exception as e:
        print(f"Error creating table {query[0]}: {e}")

def Populate_tables(cursor, Websites, items):
    stop = False
    for j,item in enumerate(items):
        print("--" * 20)
        for i,website in enumerate(Websites):
            print(f"Processing {website} - {item}")
            with open(f"Main\Products\{website}\{item}.csv", "r", newline='', encoding="utf-8") as file:
                reader = csv.DictReader(file)
                Table = Table_Queries[i + j*3][0]
                print(f"Table: {Table}")
                for row in reader:
                    #Normalizing Resolution
                    if item == "Ecran Gamer":
                        if row["Resolution"] == "1920x1080":
                            row["Resolution"] = "fhd"
                    if item == "Pc Portable Gamer":
                        if row["Screen Resolution"] == "1920x1080":
                            row["Screen Resolution"] = "fhd"
                    #Normalizing Brightness   
                    if item == "Ecran Gamer":
                        row["Brightness"] = row["Brightness"].replace(" cd/m²",'')        
                    #Normalizing Curvature
                    if item == "Ecran Gamer":
                        row["Curvature"] = row["Curvature"].replace("r",'')      
                    # print(row) 
                    Insertion_Query = ""
                    
                    if item == "Pc Portable Gamer" :
                        Insertion_Query = f"""INSERT INTO {Table} VALUES (
                                            {sql_value(row["Title"])},
                                            {clean_price(row['Price'])},
                                            {sql_value(row["Link"])},
                                            {sql_value(row["Image"])},
                                            {sql_value(row["Availability"])},
                                            {sql_value(row["ID"])},
                                            {sql_value(row["Brand"])},
                                            {sql_value(row["Model"])},
                                            {sql_value(row["CPU Brand"])},
                                            {sql_value(row["CPU Model"])},
                                            {sql_value(safe_call(int,row["CPU Cores"]))},
                                            {sql_value(safe_call(float,row["CPU Frequency"]))},
                                            {sql_value(safe_call(int,row["RAM Size"]))},
                                            {sql_value(row["RAM Type"])},
                                            {sql_value(safe_call(int,row["Storage Size"]) * 1024 if row['Storage Unit'] == "tb" and safe_call(int,row["Storage Size"]) != None else safe_call(int,row["Storage Size"]))},
                                            {sql_value(row["Storage Type"])},
                                            {sql_value(row["GPU Brand"])},
                                            {sql_value(row["GPU Model"])},
                                            {sql_value(safe_call(int,row["GPU Memory"]))},
                                            {sql_value(safe_call(int,row["Wi-Fi"]))},
                                            {sql_value(safe_call(int,row["Bluetooth"]))},
                                            {sql_value(row["Keyboard"])},
                                            {sql_value(row["Screen Type"])},
                                            {sql_value(safe_call(float,row["Screen Size"]))},
                                            {sql_value(Resolution(row["Screen Resolution"]))},
                                            {sql_value(safe_call(int,row["Screen Refresh Rate"]))}
                                        )
                                        ON CONFLICT (link) DO UPDATE SET
                                            title = {sql_value(row["Title"])},
                                            price = {clean_price(row['Price'])},
                                            image = {sql_value(row["Image"])},
                                            availability = {sql_value(row["Availability"])},
                                            site_id = {sql_value(row["ID"])},
                                            brand = {sql_value(row["Brand"])},
                                            model = {sql_value(row["Model"])},
                                            cpu_brand = {sql_value(row["CPU Brand"])},
                                            cpu_model = {sql_value(row["CPU Model"])},
                                            cpu_cores = {sql_value(safe_call(int,row["CPU Cores"]))},
                                            cpu_frequency = {sql_value(safe_call(float,row["CPU Frequency"]))},
                                            ram_size = {sql_value(safe_call(int,row["RAM Size"]))},
                                            ram_type = {sql_value(row["RAM Type"])},
                                            storage_size = {sql_value(safe_call(int,row["Storage Size"]) * 1024 if row['Storage Unit'] == "tb" and safe_call(int,row["Storage Size"]) != None else safe_call(int,row["Storage Size"]))},
                                            storage_type = {sql_value(row["Storage Type"])},
                                            gpu_brand = {sql_value(row["GPU Brand"])},
                                            gpu_model = {sql_value(row["GPU Model"])},
                                            gpu_memory = {sql_value(safe_call(int,row["GPU Memory"]))},
                                            wifi = {sql_value(safe_call(int,row["Wi-Fi"]))},
                                            bluetooth = {sql_value(safe_call(int,row["Bluetooth"]))},
                                            keyboard = {sql_value(row["Keyboard"])},
                                            screen_type = {sql_value(row["Screen Type"])},
                                            screen_size = {sql_value(safe_call(float,row["Screen Size"]))},
                                            screen_resolution = {sql_value(Resolution(row["Screen Resolution"]))},
                                            screen_refresh_rate = {sql_value(safe_call(int,row["Screen Refresh Rate"]))};
                                        """
                    if item == "Pc de Bureau Gamer":
                        Insertion_Query = f"""INSERT INTO {Table} VALUES (
                                                {sql_value(row["Title"])},
                                                {clean_price(row['Price'])},
                                                {sql_value(row["Link"])},
                                                {sql_value(row["Image"])},
                                                {sql_value(row["Availability"])},
                                                {sql_value(row["ID"])},
                                                {sql_value(row["CPU Brand"])},
                                                {sql_value(row["CPU Model"])},
                                                {sql_value(safe_call(int,row["CPU Cores"]))},
                                                {sql_value(safe_call(float,row["CPU Frequency"]))},
                                                {sql_value(safe_call(int,row["RAM Size"]))},
                                                {sql_value(row["RAM Type"])},
                                                {sql_value(safe_call(int,row["Storage Size"]) * 1024 if row['Storage Unit'] == "tb" and safe_call(int,row["Storage Size"]) != None else sql_value(safe_call(int,row["Storage Size"])))},
                                                {sql_value(row["Storage Type"])},
                                                {sql_value(row["GPU Brand"])},
                                                {sql_value(row["GPU Model"])},
                                                {sql_value(safe_call(int,row["GPU Memory"]))}
                                            )
                                            ON CONFLICT (link) DO UPDATE SET
                                                title = {sql_value(row["Title"])},
                                                price = {clean_price(row['Price'])},
                                                image = {sql_value(row["Image"])},
                                                availability = {sql_value(row["Availability"])},
                                                site_id = {sql_value(row["ID"])},
                                                cpu_brand = {sql_value(row["CPU Brand"])},
                                                cpu_model = {sql_value(row["CPU Model"])},
                                                cpu_cores = {sql_value(safe_call(int,row["CPU Cores"]))},
                                                cpu_frequency = {sql_value(safe_call(float,row["CPU Frequency"]))},
                                                ram_size = {sql_value(safe_call(int,row["RAM Size"]))},
                                                ram_type = {sql_value(row["RAM Type"])},
                                                storage_size = {sql_value(safe_call(int,row["Storage Size"]) * 1024 if row['Storage Unit'] == "tb" and safe_call(int,row["Storage Size"]) != None else sql_value(safe_call(int,row["Storage Size"])))},
                                                storage_type = {sql_value(row["Storage Type"])},
                                                gpu_brand = {sql_value(row["GPU Brand"])},
                                                gpu_model = {sql_value(row["GPU Model"])},
                                                gpu_memory = {sql_value(safe_call(int,row["GPU Memory"]))};
                                            """
                    if item == "Ecran Gamer":
                        Insertion_Query = f"""INSERT INTO {Table} VALUES (
                                            {sql_value(row["Title"])},
                                            {clean_price(row['Price'])},
                                            {sql_value(row["Link"])},
                                            {sql_value(row["Image"])},
                                            {sql_value(row["Availability"])},
                                            {sql_value(row["ID"])},
                                            {sql_value(row["Brand"])},
                                            {sql_value(row["Panel Type"])},
                                            {sql_value(safe_call(float, row["Size"]))},
                                            {sql_value(Resolution(row["Resolution"]))},
                                            {sql_value(safe_call(int, row["Refresh Rate"]))},
                                            {sql_value(safe_call(int, re.search(r'\d+', row["Response Time"]).group()) if re.search(r'\d+', row["Response Time"]) else None)},
                                            {sql_value(row["Contrast"])},
                                            {sql_value(safe_call(int, brightness(row["Brightness"])) )},
                                            {sql_value(row["Viewing Angle"])},
                                            {sql_value(safe_call(int, curvature(row["Curvature"])) )},
                                            {sql_value(row["Audio Ports"] == "Yes")},
                                            {sql_value(row["Flicker Free"] == "Yes")},
                                            {sql_value(row["Blue Light Filter"] == "Yes")},
                                            {sql_value(row["Adaptive Sync"] == "Yes")}
                                        )
                                        ON CONFLICT (link) DO UPDATE SET
                                            title = {sql_value(row["Title"])},
                                            price = {clean_price(row['Price'])},
                                            image = {sql_value(row["Image"])},
                                            availability = {sql_value(row["Availability"])},
                                            site_id = {sql_value(row["ID"])},
                                            brand = {sql_value(row["Brand"])},
                                            panel_type = {sql_value(row["Panel Type"])},
                                            size = {sql_value(safe_call(float, row["Size"]))},
                                            resolution = {sql_value(Resolution(row["Resolution"]))},
                                            refresh_rate = {sql_value(safe_call(int, row["Refresh Rate"]))},
                                            response_time = {sql_value(safe_call(int, re.search(r'\d+', row["Response Time"]).group()) if re.search(r'\d+', row["Response Time"]) else None)},
                                            contrast = {sql_value(row["Contrast"])},
                                            brightness = {sql_value(safe_call(int, brightness(row["Brightness"])) )},
                                            viewing_angle = {sql_value(row["Viewing Angle"])},
                                            curvature = {sql_value(safe_call(int, curvature(row["Curvature"])) )},
                                            audio_ports = {sql_value(row["Audio Ports"] == "Yes")},
                                            flicker_free = {sql_value(row["Flicker Free"] == "Yes")},
                                            blue_light_filter = {sql_value(row["Blue Light Filter"] == "Yes")},
                                            adaptive_sync = {sql_value(row["Adaptive Sync"] == "Yes")};
                                        """
                    # Execute the insertion query
                    try:
                        cursor.execute(Insertion_Query)
                        print(f"Inserted data into {Table}: {row['Title']} \n {clean_price(row['Price'])}")
                    except Exception as e:
                        print(f"Error inserting data into {Table}: {e}")
                        stop = True
                        break
                    print("." * 20) 
                    
                # Create a list of links from the CSV file
                # Reset the file pointer to the beginning to read the rows again
                file.seek(0)
                reader = csv.DictReader(file)
                links = [row["Link"] for row in reader]
                print(f"Links: {len(links)}")
                # print(','.join([sql_value(link) for link in links]))
                # Generate the deletion query using the Python list
                Obsolete_products = f"DELETE FROM {Table} WHERE link NOT IN ({','.join([sql_value(link) for link in links])});"
                cursor.execute(Obsolete_products)
                
        if stop:
            break            


#Normalizing data entered into the tables
def sql_value(val):
    if val is None or val == "Unknown":
        return "NULL"
    if isinstance(val, str):
        return f"'{val.replace("'", "''")}'"
    return str(val)
    
def clean_price(price_str):
    # Remove non-breaking spaces and normal spaces
    price_str = price_str.replace('\xa0', '').replace(' ', '')
    if ',' in price_str:
        price_str = price_str.split(',')[0]
    # Remove currency and any non-digit, non-comma, non-dot
    price_str = re.sub(r'[^\d]', '', price_str)
    # If there's a comma, keep only the part before the comma (thousands separator)
    if ',' in price_str:
        price_str = price_str.split(',')[0]
    try:
        return int(price_str)
    except ValueError:
        return "NULL"
    
def refresh_rate(s):
    try:
        return int(re.search(r'\d+', s).group())
    except:
        return None

def response_time(s):
    try:
        return int(re.search(r'\d+', s).group()) if re.search(r'\d+', s) else None
    except:
        return None

def brightness(s):
    try:
        return int(s.split(" ")[0])
    except:
        return None

def curvature(s):
    try:
        if s != "Unknown":
            return int(re.sub(r'\D', '', s))
    except:
        return None

def safe_call(f, s):
    try:
        return f(s)
    except:
        return None

def Resolution(s):
    s = s.replace(" ", "")
    if s in ["1920x1080","fhd"]:
        return "fhd"
    elif s in ["1366x768","hd"]:
        return "hd"
    elif s in ["2560x1440", "qhd"]:
        return "qhd"
    elif s in ["3840x2160", "uhd"]:
        return "uhd"
    else:
        return None

def main():
    # Load environment variables
    load_dotenv()
    # Connect to the database
    DB = psycopg2.connect(
        host=os.getenv("dbhost"),
        dbname=os.getenv("dbname"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpass"),
        port=os.getenv("dbport")
    )
    cursor = DB.cursor()
    # Create tables if they do not exist
    for table in Table_Queries:
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table[0]}'")
        if cursor.fetchone() is not None:
            print(f"Table {table[0]} already exists.")
        else:
            cursor.execute(table[1])
            print(f"Table {table[0]} created.")
    # Websites and items to process
    items = ["Pc Portable Gamer", "Pc de Bureau Gamer", "Ecran Gamer"]
    Websites = ["Tunisianet","Mytek","Scoop Gaming"]
    # Updating the tables
    print("Updating Tables")
    Populate_tables(cursor, Websites, items)
    # Commit the changes to the database
    DB.commit()
    print("Finished Inserting Data")
    cursor.close()
    DB.close()