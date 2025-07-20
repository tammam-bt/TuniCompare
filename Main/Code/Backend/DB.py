import psycopg2
import csv
import re

DB = psycopg2.connect(host = "localhost", dbname = "Site_Comparator_DB", user = "postgres", password = "TMPhoenix4101920", port = 5432)
cursor = DB.cursor()


#Creating Tables

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

# for query in Table_Queries:
#     try:
#         cursor.execute(query[1])
#         print("Created Table " + query[0])
#     except Exception as e:
#         print(f"Error creating table {query[0]}: {e}")


#Filling the tables with data
def sql_value(val):
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return f"'{val.replace("'", "''")}'"
    return str(val)
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
        print(s.split(" ")[0])
        return int(s.split(" ")[0])
    except:
        return None

def curvature(s):
    try:
        print(s.replace("r", ""))
        return int(s.replace("r", ""))
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
    
items = ["Pc Portable Gamer", "Pc de Bureau Gamer", "Ecran Gamer"]
Websites = ["Tunisianet","Mytek","Scoop Gaming"]
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
                print(f"Processing row: {row}")
                #Normalizing Price
                row['Price'] = row['Price'].replace("TND",'')
                row['Price'] = row['Price'].replace("\xa0",'')
                row['Price'] = row['Price'].replace(",",'')
                row['Price'] = row['Price'].replace("\u202f",'')
                row['Price'] = row['Price'][:-3]
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

                                        {sql_value(safe_call(int, row['Price']))},
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
                                    );
                                    """
                if item == "Pc de Bureau Gamer":
                    Insertion_Query = f"""INSERT INTO {Table} VALUES (
                                            {sql_value(row["Title"])},

                                            {sql_value(safe_call(int, row['Price']))},
                                            
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
                                        );
                                        """
                if item == "Ecran Gamer":
                    Insertion_Query = f"""INSERT INTO {Table} VALUES (
                                        {sql_value(row["Title"])},

                                        {sql_value(safe_call(int, row['Price']))},
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
                                    );
                                    """  
                # Execute the insertion query
                try:
                    cursor.execute(Insertion_Query)
                    # print(f"Inserted data into {Table}: {row['Title']}")
                except Exception as e:
                    print(f"Error inserting data into {Table}: {e}")
                    stop = True
                    break
                print("." * 20)    
    if stop:
        break            

DB.commit()
print("Finished Inserting Data")
cursor.close()
DB.close()