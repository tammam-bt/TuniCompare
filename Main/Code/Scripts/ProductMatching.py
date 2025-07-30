#This file contains all the logic necessary to creating a table for each product category.
#It contains all the matching logic for products, including the logic to match products based on their specifications.

from thefuzz import fuzz
import psycopg2
import re
from dotenv import load_dotenv
import os



def sql_value(val):
    if val is None:
        return "NULL"
    if isinstance(val, str):
        return f"'{val.replace("'", "''")}'"
    return str(val)

def check_screen_size(screen_size1, screen_size2):
    """
    Check if two screen sizes are similar enough to be considered a match.
    """
    try:
        return abs(screen_size1 - screen_size2) <= 0.5  # Allow a difference of 0.5 inches
    except ValueError:
        return False

def Insert_Product(cursor, product_type, link1, link2 = None, link3 = None):
    """
    Inserts a product in the database.
    """
    cursor.execute(f"""INSERT INTO Matched_{product_type}
                        (linkTunisianet, linkMytek, linkScoopGaming)
                        VALUES ({sql_value(link1)}, {sql_value(link2)}, {sql_value(link3)})
                        ON CONFLICT (linkTunisianet)
                        DO UPDATE SET linkMytek = {sql_value(link2)}, linkScoopGaming = {sql_value(link3)};""")
    print(f"Updated {product_type} product with links: {link1}, {link2}, {link3}")

def Pull_Data(Website, product_type, cursor, where_clause=None):
    """
    Pulls the laptops from the website and returns them as a list of dictionaries.
    """
    cursor.execute(f"SELECT * FROM {Website}_{product_type} {where_clause};")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

def normalize_string(s):
    # Remove special characters and extra spaces
    s = re.sub(r'[^\w\s",.-]', ' ', s) # Remove special characters except for common punctuation
    s = re.sub(r'\s+', ' ', s).strip() # Replace multiple spaces with a single space and strip leading/trailing spaces
    s = re.sub(r'(\d+)([a-zA-Z]+)', lambda m: f"{m.group(1)}{m.group(2)}" if len(m.group(2))==1 else f"{m.group(1)} {m.group(2)}", s)  # Add space between numbers and words (e.g., "16Go" to "16 Go")
    s = s.replace(" ", " ")  # Replace non-breaking spaces with regular spaces
    s = s.lower()  # Convert to lowercase
    s = re.sub(r'\s*(pc portable gamer|pc portable gaming|pc portable|pc|portable|laptop|gaming|gamer)\s*', '', s)  # remove PC terms
    s = re.sub(r'amd ryzen', 'ryzen', s)  # Normalize AMD Ryzen
    s = s.replace("octa-core", "octacore")  # Normalize Octa-Core7
    s = s.replace("hexa-core", "hexacore")  # Normalize Hexa-Core
    s = s.replace("quad-core", "quadcore")  # Normalize Quad-Core
    s = s.replace("octa core", "octacore")  # Normalize Octa-Core7
    s = s.replace("hexa core", "hexacore")  # Normalize Hexa-Core
    s = s.replace("quad core", "quadcore")  # Normalize Quad-Core
    s = s.replace("quad", "4 ")  # Normalize Quad to 4
    s = s.replace("hexa", "6 ")  # Normalize Hexa to 6 
    s = s.replace("octa", "8 ")  # Normalize Octa to 8
    s = re.sub(r'(\bgo\b)','gb',s)   # Normalize Go to GB
    s = re.sub(r'(\bmo\b)','mb',s)   # Normalize Mo to MB
    s= re.sub(r'(?<!up\s)(\bto\b)','tb',s)   # Normalize To to TB
    s = s.replace("ssd nvme", "nvme ssd")  # Normalize SSD
    s = s.replace("full hd", "fhd")  # Normalize Full HD
    s = s.replace("wi-fi", "wifi")  # Normalize Wi-Fi
    s = s.replace("pavé", "clavier")  # Normalize Clavier
    s = s.replace("carte graphique", "gpu")  # Normalize Carte Graphique
    s = s.replace("graphique", "gpu")  # Normalize Carte Graphique
    s = s.replace("processeur", "cpu")  # Normalize Processeur
    s = s.replace("écran", "ecran")  # Normalize Ecran
    s = s.replace("mémoire ram", "ram")  # Normalize Mémoire RAM
    s = s.replace("jusqu à", "up to")
    return s

def specs_similarity_ecran(specs1, specs2):
    """
    Calculate the similarity score between two ecran specifications.
    """
    score = 0
    if specs1["brand"] != None and specs2["brand"] != None:
        if fuzz.token_set_ratio(specs1["brand"], specs2["brand"]) > 90:
            print(f"Matched Specs1: {specs1['brand']}, Specs2: {specs2['brand']} --- " , fuzz.token_set_ratio(specs1["brand"], specs2["brand"]))
            score += 10
    if specs1["panel_type"] != None and specs2["panel_type"] != None:
        if specs1["panel_type"] == specs2["panel_type"]:
            print(f"Matched Specs1: {specs1['panel_type']}, Specs2: {specs2['panel_type']} --- " , fuzz.token_set_ratio(specs1["panel_type"], specs2["panel_type"]))
            score += 10
        else:
            print("Panel Type mismatch")
            print(f"Specs1: {specs1['panel_type']}, Specs2: {specs2['panel_type']}" , fuzz.token_set_ratio(specs1["panel_type"], specs2["panel_type"]))
            return 0
    if specs1["size"] != None and specs2["size"] != None:
        if (fuzz.token_set_ratio(specs1["size"], specs2["size"]) > 90 or check_screen_size(specs1["size"], specs2["size"])):
            print(f"Matched Specs1: {specs1['size']}, Specs2: {specs2['size']} --- " , fuzz.token_set_ratio(specs1["size"], specs2["size"]))
            score += 10
        else:
            print("Size mismatch")
            print(f"Specs1: {specs1['size']}, Specs2: {specs2['size']}")
            return 0
    if specs1["resolution"] != None and specs2["resolution"] != None:
        if  fuzz.token_set_ratio(specs1["resolution"], specs2["resolution"]) > 90:
            score += 10
        else:
            print("Resolution mismatch")
            print(f"Specs1: {specs1['resolution']}, Specs2: {specs2['resolution']}")
            return 0
    if specs1["refresh_rate"] != None and specs2["refresh_rate"] != None:
        if fuzz.token_set_ratio(specs1["refresh_rate"], specs2["refresh_rate"]) > 90:
            score += 10
        else:
            print("Refresh Rate mismatch")
            print(f"Specs1: {specs1['refresh_rate']}, Specs2: {specs2['refresh_rate']}")
            return 0
    return (score / 50)*100  # Normalize the score to a percentage

def specs_similarity_pc_bureau(specs1, specs2):
    """
    Calculate the similarity score between two pc bureau specifications.
    """
    score = 0
    max_score = 75  # Maximum score for PC Bureau specifications
    print(f"Specs1: {specs1['cpu_brand']} {specs1['cpu_model']}, Specs2: {specs2['cpu_brand']} {specs2['cpu_model']}")
    if specs1["cpu_brand"] != None and specs2["cpu_brand"] != None:
        if specs1["cpu_brand"] == specs2["cpu_brand"]:
            score += 10
            if specs1["cpu_model"] != None and specs2["cpu_model"] != None:
                if fuzz.token_set_ratio(specs1["cpu_model"], specs2["cpu_model"]) > 90:
                    print(f"Matched Specs1: {specs1['cpu_model']}, Specs2: {specs2['cpu_model']} --- " , fuzz.token_set_ratio(specs1["cpu_model"], specs2["cpu_model"]))
                    score += 20
                else:
                    print("CPU Model mismatch")
                    print(f"Specs1: {specs1['cpu_model']}, Specs2: {specs2['cpu_model']}")
                    return 0    
                if specs1["cpu_cores"] != None and specs2["cpu_cores"] != None:
                    if specs1["cpu_cores"] == specs2["cpu_cores"]:
                        score += 5
                else:
                    max_score -= 5        
            else:
                max_score -= 20  # Deduct points if CPU model is missing
        else:
            print("CPU Brand mismatch")
            return 0 
    else:
        max_score -= 10  # Deduct points if CPU brand is missing      
    print(f"Specs1: {specs1['ram_size']}, Specs2: {specs2['ram_size']}")               
    if specs1["ram_size"] != None and specs2["ram_size"] != None:
        if specs1["ram_size"] == specs2["ram_size"]:
            score += 10
        else:
            print("RAM Size mismatch")
            return 0  
    else:
        max_score -= 10          
    print(f"Specs1: {specs1['gpu_brand']} {specs1['gpu_model']}, Specs2: {specs2['gpu_brand']} {specs2['gpu_model']}")    
    if specs1["gpu_brand"] != None and specs2["gpu_brand"] != None:
        if specs1["gpu_brand"] == specs2["gpu_brand"]:
            score += 10
            if specs1["gpu_model"] != None and specs2["gpu_model"] != None:
                if fuzz.token_set_ratio(specs1["gpu_model"].replace("-", ""), specs2["gpu_model"].replace("-", "")) > 90:
                    score += 20
                    if specs1["gpu_memory"] != None and specs2["gpu_memory"] != None:
                        if specs1["gpu_memory"] == specs2["gpu_memory"]:
                            score += 10
                    else:
                        max_score -= 10
                else:
                    print("GPU Model mismatch")
                    print(f"Specs1: {specs1['gpu_model']}, Specs2: {specs2['gpu_model']}")
                    return 0
            else:
                max_score -= 20  # Deduct points if GPU model is missing
        else:
            print("GPU Brand or Model mismatch")
            return 0  
    else:
        max_score -= 10        
    print(f"Specs1: {specs1['storage_type']} {specs1['storage_size']}, Specs2: {specs2['storage_type']} {specs2['storage_size']}")                  
    if specs1["storage_type"] != None and specs2["storage_type"] != None:
        if specs1["storage_type"] == specs2["storage_type"]:
            score += 10
            if specs1["storage_size"] != None and specs2["storage_size"] != None:
                if abs(specs1["storage_size"] - specs2["storage_size"]) <= 100:
                    score += 10
                else:
                    print("Storage Size mismatch")
                    print(f"Specs1: {specs1['storage_size']}, Specs2: {specs2['storage_size']}")
                    return 0    
            else:
                max_score -= 10        
        else:
            print("Storage Type or Size mismatch")
            return 0
    else:
        max_score -= 10        
    return (score / max_score) * 100  # Normalize the score to a percentage

def specs_similarity_pc_portable(specs1, specs2):
    """
    Calculate the similarity score between two products specifications.
    """
    score = 0
    if specs1["brand"] != None and specs2["brand"] != None and fuzz.token_set_ratio(specs1["brand"], specs2["brand"]) > 90:
        score += 10
    else:
        return 0
    if specs1["cpu_brand"] != None and specs2["cpu_brand"] != None:
        if specs1["cpu_brand"] == specs2["cpu_brand"]:
            score += 10
            if specs1["cpu_model"] != None and specs2["cpu_model"] != None and specs1["cpu_model"] == specs2["cpu_model"]:
                score += 20
            if specs1["cpu_cores"] != None and specs2["cpu_cores"] != None and specs1["cpu_cores"] == specs2["cpu_cores"]:
                score += 5
        else:
            return 0        
    if specs1["ram_size"] != None and specs2["ram_size"] != None:
        if specs1["ram_size"] == specs2["ram_size"]:
            score += 10
        else:
            return 0    
    if specs1["gpu_brand"] != None and specs2["gpu_brand"] != None:
        if specs1["gpu_brand"] == specs2["gpu_brand"]:
            score += 10
            if specs1["gpu_model"] != None and specs2["gpu_model"] != None and specs1["gpu_model"] == specs2["gpu_model"]:
                score += 20
                if specs1["gpu_memory"] != None and specs2["gpu_memory"] != None and specs1["gpu_memory"] == specs2["gpu_memory"]:
                    score += 10
        else:
            return 0            
    if specs1["storage_type"] != None and specs2["storage_type"] != None and specs1["storage_type"] == specs2["storage_type"] and specs1["storage_size"] != None and specs2["storage_size"] != None and specs1["storage_size"] == specs2["storage_size"]:
        score += 10
    if specs1["screen_type"] != None and specs2["screen_type"] != None and specs1["screen_type"] == specs2["screen_type"]:
        score += 10
    if specs1["screen_size"] != None and specs2["screen_size"] != None and specs1["screen_size"] == specs2["screen_size"]:
        score += 10
    if specs1["screen_resolution"] != None and specs2["screen_resolution"] != None and specs1["screen_resolution"] == specs2["screen_resolution"]:
        score += 10
    if specs1["screen_refresh_rate"] != None and specs2["screen_refresh_rate"] != None and specs1["screen_refresh_rate"] == specs2["screen_refresh_rate"]:
        score += 10
    return (score / 145)*100  # Normalize the score to a percentage   

def similarity_score(product1, product2, product_type = "Pc_Portable_Gamer"):
    """
    Calculate the similarity score between two titles.
    """
    if product1["site_id"] == product2["site_id"]:
        return 999
    
    # Normalize the titles
    norm_title1 = normalize_string(product1['title'])
    # print(f"Normalized Title 1: {norm_title1}")
    norm_title2 = normalize_string(product2['title'])
    # print(f"Normalized Title 2: {norm_title2}")

    # Calculate the similarity score
    fuzzscore = fuzz.token_set_ratio(norm_title1, norm_title2) # Using token set ratio for better matching
    
    # print(f"Fuzz Score: {fuzzscore}")
    if product_type == "Pc_Bureau_Gamer":
        specs_score = specs_similarity_pc_bureau(product1, product2)  # Example specs comparison, replace with actual specs extraction logic
        return specs_score
    elif product_type == "Pc_Portable_Gamer":    
        specs_score = specs_similarity_pc_portable(product1, product2)  # Example specs comparison, replace with actual specs extraction logic
        if specs_score == 0:
            return 0
        else:
            # print(f"Specs Score: {specs_score}")
            return (fuzzscore + specs_score) / 2
    elif product_type == "Ecran_Gamer":
        specs_score = specs_similarity_ecran(product1, product2)  # Example specs comparison, replace with actual specs extraction logic
        return (fuzzscore + specs_score) / 2

def Create_Table(cursor, query):
    # Create a table in the database
    try:
        cursor.execute(query[1])
        print("Created Table " + query[0])
    except Exception as e:
        print(f"Error creating table {query[0]}: {e}")

# Table Creation Queries
Matched_Pc_Portable_Gamer = ["Matched_Pc_Portable_Gamer", """CREATE TABLE IF NOT EXISTS Matched_Pc_Portable_Gamer (
linkTunisianet text PRIMARY KEY,
linkMytek text,
linkScoopGaming text,
FOREIGN KEY (linkTunisianet) REFERENCES Tunisianet_Pc_Portable_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkMytek) REFERENCES Mytek_Pc_Portable_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkScoopGaming) REFERENCES ScoopGaming_Pc_Portable_Gamer(link) ON DELETE CASCADE
);
"""]

Matched_Pc_Bureau_Gamer = ["Matched_Pc_Bureau_Gamer", """CREATE TABLE IF NOT EXISTS Matched_Pc_Bureau_Gamer (
linkTunisianet text PRIMARY KEY,
linkMytek text,
linkScoopGaming text,
FOREIGN KEY (linkTunisianet) REFERENCES Tunisianet_Pc_Bureau_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkMytek) REFERENCES Mytek_Pc_Bureau_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkScoopGaming) REFERENCES ScoopGaming_Pc_Bureau_Gamer(link) ON DELETE CASCADE
);
"""]

Matched_Ecran_Gamer = ["Matched_Ecran_Gamer","""CREATE TABLE IF NOT EXISTS Matched_Ecran_Gamer (
linkTunisianet text PRIMARY KEY,
linkMytek text,
linkScoopGaming text,
FOREIGN KEY (linkTunisianet) REFERENCES Tunisianet_Ecran_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkMytek) REFERENCES Mytek_Ecran_Gamer(link) ON DELETE CASCADE,
FOREIGN KEY (linkScoopGaming) REFERENCES ScoopGaming_Ecran_Gamer(link) ON DELETE CASCADE
);
"""]

Table_Queries = [Matched_Pc_Portable_Gamer, Matched_Pc_Bureau_Gamer, Matched_Ecran_Gamer]

def main():
    # Load environment variables from .env file
    load_dotenv()
    # Create a connection to the database
    DB = psycopg2.connect(
        host=os.getenv("dbhost"),
        dbname=os.getenv("dbname"),
        user=os.getenv("dbuser"),
        password=os.getenv("dbpass"),
        port=os.getenv("dbport")
    )
    cursor = DB.cursor()
    # Product Types and Websites
    product_types = ["Pc_Portable_Gamer", "Pc_Bureau_Gamer", "Ecran_Gamer"]
    Websites = ["Tunisianet", "Mytek", "ScoopGaming"]

    for table in Table_Queries:
        cursor.execute(f"SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table[0]}'")
        if cursor.fetchone() is not None:
            print(f"Table {table[0]} already exists.")
        else:
            Create_Table(cursor, table)
            print(f"Table {table[0]} created.")
         
    # Pull data from each website for each product type
    Mytek_Pc_Portable_Gamer = Pull_Data("Mytek", "Pc_Portable_Gamer", cursor)
    Tunisianet_Pc_Portable_Gamer = Pull_Data("Tunisianet", "Pc_Portable_Gamer", cursor)
    ScoopGaming_Pc_Portable_Gamer = Pull_Data("ScoopGaming", "Pc_Portable_Gamer", cursor)
    Mytek_Pc_Bureau_Gamer = Pull_Data("Mytek", "Pc_Bureau_Gamer", cursor)
    Tunisianet_Pc_Bureau_Gamer = Pull_Data("Tunisianet", "Pc_Bureau_Gamer", cursor)
    ScoopGaming_Pc_Bureau_Gamer = Pull_Data("ScoopGaming", "Pc_Bureau_Gamer", cursor)
    Mytek_Ecran_Gamer = Pull_Data("Mytek", "Ecran_Gamer", cursor)
    Tunisianet_Ecran_Gamer = Pull_Data("Tunisianet", "Ecran_Gamer", cursor)
    ScoopGaming_Ecran_Gamer = Pull_Data("ScoopGaming", "Ecran_Gamer", cursor)

    print("Data pulled successfully.")


    # Iterate through each product type
    i = 0
    for product_type in product_types:
        # Get the products for each type
        if product_type == "Pc_Portable_Gamer":
            Mytek_Products = Mytek_Pc_Portable_Gamer
            Tunisianet_Products = Tunisianet_Pc_Portable_Gamer
            ScoopGaming_Products = ScoopGaming_Pc_Portable_Gamer
        elif product_type == "Pc_Bureau_Gamer":
            Mytek_Products = Mytek_Pc_Bureau_Gamer
            Tunisianet_Products = Tunisianet_Pc_Bureau_Gamer
            ScoopGaming_Products = ScoopGaming_Pc_Bureau_Gamer
        elif product_type == "Ecran_Gamer":
            Mytek_Products = Mytek_Ecran_Gamer
            Tunisianet_Products = Tunisianet_Ecran_Gamer
            ScoopGaming_Products = ScoopGaming_Ecran_Gamer

        # Match products from Tunisianet with Mytek
        for product1 in Tunisianet_Products:
            Mytek = False
            ScoopGaming = False
            print(f"Matching product: {product1['title']}")
            max_similarity = 0
            similar_product2 = None
            for product2 in Mytek_Products:
                score = similarity_score(product1, product2, product_type)
                if score >= max_similarity:  # Adjust threshold as needed
                    max_similarity = score
                    similar_product2 = product2
            if max_similarity > 60:  # Adjust threshold as needed
                print(f"Matched from Tunisianet {product1['link']} \nwith from Mytek {similar_product2['link']} \nwith a score of {max_similarity}")
                Mytek = True
                # Matched Tunisianet with mytek
                # Let's try to match iwth ScoopGaming
            else:
                print(f"No match found for {product1['link']} with Mytek products.")
                print("Max Similarity: " + str(max_similarity))
            max_similarity = 0
            similar_product3 = None
            for product3 in ScoopGaming_Products:
                score = similarity_score(product1, product3, product_type)
                if score >= max_similarity:  # Adjust threshold as needed
                    max_similarity = score
                    similar_product3 = product3
            if max_similarity > 60:  # Adjust threshold as needed
                print(f"Matched from Tunisianet {product1['link']} \nwith from ScoopGaming {similar_product3['link']} \nwith a score of {max_similarity}")
                ScoopGaming = True
            else:
                print(f"No match found for {product1['link']} with ScoopGaming products.")
                print("Max Similarity: " + str(max_similarity))
            i += 1 if Mytek else 0
            i += 1 if ScoopGaming else 0    
            Insert_Product(cursor, product_type, product1['link'], similar_product2['link'] if Mytek else None, similar_product3['link'] if ScoopGaming else None)    
            print("----" * 50)
        print(f"Total products matched for {product_type}: {i}")
        Cleaning_Query = "DELETE FROM Matched_" + product_type + " WHERE linkTunisianet NOT IN (SELECT linktunisianet FROM Tunisianet_" + product_type + ");"
        cursor.execute(Cleaning_Query)
    DB.commit()
    print("All products matched and inserted successfully.")

    DB.close()
    cursor.close()