#This file contains all the logic necessary to creating a table for each product category.
#It contains all the matching logic for products, including the logic to match products based on their specifications.

from functools import lru_cache
from thefuzz import fuzz
import sqlite3
import re
from Scripts.DB import DB_PATH

# A Tunisianet listing and a store listing count as the same product when they score at least this (out of 100)
MATCH_THRESHOLD = 75


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

def normalize_gpu(value):
    """Lowercase with spaces and dashes removed: 'RTX-3050', 'rtx 3050' and 'rtx3050' all become 'rtx3050'."""
    if value is None:
        return None
    return re.sub(r"[\s-]+", "", str(value).lower()) or None

def normalize_cpu(value):
    """Same as normalize_gpu, after dropping the stray clock digit Mytek appends to desktop Ryzens ('ryzen5-5500-3')."""
    if value is None:
        return None
    return normalize_gpu(re.sub(r"-\d$", "", str(value).strip().lower()))

# Tokens right after a CPU or GPU name ('i5-12450HX', 'Ultra 9 185H', 'RTX 5070Ti') are specs, not model codes
_CPU_NUMBER = re.compile(r"\b(?:i[3579]|r[3579]|ryzen ?[3579]?|core ?(?:ultra ?)?[3579]?|ultra ?[3579]|ai ?(?:max\+? ?)?[3579]?(?: hx)?)[ -]*(\d[a-z0-9]*)")
_GPU_NUMBER = re.compile(r"\b(?:rtx|gtx|gt|rx|mx|arc|radeon|vega)[ -]*(\d[a-z0-9]*)")
# RAM and storage sizes, DDR generations, GPU names, and refresh rate, response time, resolution and curvature values
_NOT_A_MODEL_CODE = re.compile(r"^(?:\d+(?:go|gb|g|to|tb|mo|mb|hz|ghz|ms|p|r)|(?:lp)?ddr\d+x?|ryzen\d|(?:rtx|gtx|gt|rx|mx)\d+[a-z]*)$")

@lru_cache(maxsize=None)
def _model_codes(title):
    text = title.lower()
    specs = set(_CPU_NUMBER.findall(text)) | set(_GPU_NUMBER.findall(text))
    return frozenset(
        token for token in re.findall(r"[a-z0-9]+", text)
        if len(token) >= 4 and re.search(r"[a-z]", token) and re.search(r"\d", token)
        and token not in specs and not _NOT_A_MODEL_CODE.match(token)
    )

def model_codes(title):
    """Lowercase tokens of 4+ characters mixing letters and digits ('15IAX9', 'GA2711'), minus CPU, GPU, RAM and storage tokens."""
    return set(_model_codes(title))

def codes_compatible(codes1, codes2):
    """False when both titles carry model codes and none of them agree. One code may extend the other ('B13U' / 'B13UCX')."""
    if not codes1 or not codes2:
        return True
    return any(code1 in code2 or code2 in code1 for code1 in codes1 for code2 in codes2)

_BRANDS = re.compile(r"\b(asus|msi|hp|lenovo|dell|acer|gigabyte|razer|alienware|samsung|lg|aero|redragon|iiyama|aiwa|cooler master|dahua|philips|aoc|benq|viewsonic|xiaomi)\b")

@lru_cache(maxsize=None)
def title_brand(title):
    found = _BRANDS.search(title.lower())
    return found.group(1) if found else None

@lru_cache(maxsize=None)
def title_cpu(title):
    """(family, generation, model) from a title such as 'i5-13420H', 'i7 13è Gén', 'Ultra 9 185H' or 'Ryzen 5 7535HS'.
    Parts the title doesn't give are None; None overall when no CPU is named."""
    text = title.lower()
    found = re.search(r"\bi([3579])[ -]?(\d{4,5})([a-z]*)", text)
    if found:
        number = found.group(2)
        return ("i" + found.group(1), number[:len(number) - 3], number + found.group(3))
    found = re.search(r"\bi([3579])[ -]?(\d{1,2}) ?(?:è|é|e|th)", text)
    if found:
        return ("i" + found.group(1), found.group(2), None)
    found = re.search(r"\b(ultra|core) ?([3579])[ -]?(\d{3})([a-z]*)", text)
    if found:
        return (found.group(1) + found.group(2), found.group(3)[0], found.group(3) + found.group(4))
    found = re.search(r"\ba[il] ?(max\+?)? ?([3579])? ?(?:hx ?)?(\d{3})?\b", text)  # Ryzen AI 9 HX 370, Ryzen AI MAX+ 395
    if found and ("ryzen" in text or found.group(3)):
        family = "ryzenai" + ("max" if found.group(1) else "") + (found.group(2) or "")
        return (family, None, found.group(3))
    found = re.search(r"\bryzen ?([3579])\b(?:[ -]?(\d{4})[ -]?([a-z0-9]*))?", text)
    if found:
        number = found.group(2)
        return ("ryzen" + found.group(1), number[0] if number else None, number + found.group(3) if number else None)
    found = re.search(r"\bi([3579])\b", text)  # 'I5' alone, as Scoop Gaming writes it
    if found:
        return ("i" + found.group(1), None, None)
    return None

def cpus_conflict(cpu1, cpu2):
    if cpu1 is None or cpu2 is None:
        return False
    return any(part1 is not None and part2 is not None and part1 != part2 for part1, part2 in zip(cpu1, cpu2))

def exact_cpu(product):
    """The exact CPU ('i512400f', 'ryzen57535hs') from the cpu_model column, else from the title; None if neither names the model."""
    column = normalize_cpu(product["cpu_model"])
    if column:
        return column
    cpu = title_cpu(product["title"])
    return cpu[0] + cpu[2] if cpu and cpu[2] else None

@lru_cache(maxsize=None)
def title_gpu(title):
    """The dedicated GPU named in a title, with its Ti/Super/XT suffix: 'RTX 5060 Ti 8G' gives 'rtx5060ti'."""
    found = re.search(r"\b(rtx|gtx|gt|rx)[ -]?(\d{3,4})(?:[ -]?(ti|super|xtx|xt))?\b", title.lower())
    return "".join(part for part in found.groups() if part) if found else None

_GPU_MEMORY_SIZES = {2, 3, 4, 6, 8, 10, 12, 16, 20, 24, 32}

@lru_cache(maxsize=None)
def title_gpu_memory(title):
    """GPU memory in Go: the first size after the GPU name in its '/' or ',' segment ('RTX 3050 6G', 'RTX5060 Ti 16G')."""
    for segment in re.split(r"[/,]", title.lower()):
        gpu = re.search(r"\b(?:rtx|gtx|gt|rx)\b|\b(?:rtx|gtx)\d", segment)
        if gpu:
            found = re.search(r"\b(\d{1,2}) ?(?:go|gb|g)\b", segment[gpu.end():])
            return int(found.group(1)) if found and int(found.group(1)) in _GPU_MEMORY_SIZES else None
    return None

_RAM_SIZES = {4, 8, 12, 16, 24, 32, 48, 64, 96, 128}

@lru_cache(maxsize=None)
def title_ram(title):
    """RAM size in Go from a title. Sizes after a GPU name in the same '/' or ',' segment are GPU memory, and SSD sizes are skipped."""
    for segment in re.split(r"[/,]", title.lower()):
        gpu = re.search(r"\b(?:rtx|gtx|gt|rx|radeon|vega|arc)\b|\b(?:rtx|gtx)\d", segment)
        before_gpu = segment[:gpu.start()] if gpu else segment
        for found in re.finditer(r"\b(\d{1,3}) ?(?:go|gb|g)\b(?! ?(?:ssd|hdd|nvme|emmc))", before_gpu):
            if int(found.group(1)) in _RAM_SIZES:
                return int(found.group(1))
    return None

def title_panel(title):
    found = re.search(r"\b(ips|va|tn|oled)\b", title.lower())
    return found.group(1) if found else None

def is_setup(title):
    """Tunisianet sells 'Setup' desktops bundled with a monitor."""
    return bool(re.search(r"\bsetup\b|\bavec [ée]cran\b|\+ ?[ée]cran", title.lower()))

_WINDOWS_PRO = re.compile(r"w11 ?p|windows 11 pro|win ?11 ?pro")
# Tunisianet also marks a Windows licence with a '-W' or '-WW' ref segment. Its laptops with that segment all say
# 'Windows 11 Pro' in the title; its desktops keep the plain build's title and cost 140 to 450 DT more
_WINDOWS_REF_SEGMENT = re.compile(r"(?:^|-)ww?(?=-|$)")

def windows_bundle(product):
    """True when the offer includes a Windows licence the store adds: 'Windows 11 Pro' in the title, or a ref with
    'W11P' or a '-W'/'-WW' segment. Mytek marks it only in the ref ('[BU-...-W11P]'). Unmarked listings are plain offers."""
    ref = (product["site_id"] or "").strip("[] ").lower()
    return bool(_WINDOWS_PRO.search(f"{product['title']} {ref}".lower()) or _WINDOWS_REF_SEGMENT.search(ref))

def laptop_brand(product):
    return title_brand(product["title"]) or product["brand"]

def desktop_ram_type(product):
    """'ddr4' or 'ddr5', from the title ('32 Go DDR5'), else the ram_type column."""
    found = re.search(r"\bddr(\d)\b", product["title"].lower())
    if found:
        return "ddr" + found.group(1)
    return (product["ram_type"] or "").strip().lower() or None

def conflicting(value1, value2):
    return value1 is not None and value2 is not None and value1 != value2

def conflicting_sources(column1, column2, title1, title2):
    """Conflict between the columns, between the titles, or between each side's column-else-title value."""
    return (conflicting(column1, column2) or conflicting(title1, title2)
            or conflicting(column1 if column1 is not None else title1, column2 if column2 is not None else title2))

def spec_conflict(product1, product2, product_type):
    """Why two listings can't be the same product, or None. Only specs known on both sides are compared."""
    title1, title2 = product1["title"], product2["title"]
    if not codes_compatible(_model_codes(title1), _model_codes(title2)):
        return "model code"
    if product_type == "Ecran_Gamer":
        if conflicting(title_brand(title1), title_brand(title2)):
            return "brand"
        if conflicting(title_panel(title1) or product1["panel_type"], title_panel(title2) or product2["panel_type"]):
            return "panel"
        return None
    if product_type == "Pc_Portable_Gamer" and conflicting(laptop_brand(product1), laptop_brand(product2)):
        return "brand"
    if conflicting(normalize_gpu(product1["gpu_model"]), normalize_gpu(product2["gpu_model"])) or conflicting(title_gpu(title1), title_gpu(title2)):
        return "gpu"
    # Store-built desktops pair one GPU with several memory sizes (RTX 3050 6G/8G, RTX 5060 Ti 8G/16G).
    # A laptop's model fixes its GPU memory, and the laptop gpu_memory columns are unreliable, so laptops skip this check
    if product_type == "Pc_Bureau_Gamer" and conflicting_sources(
            product1["gpu_memory"], product2["gpu_memory"], title_gpu_memory(title1), title_gpu_memory(title2)):
        return "gpu memory"
    if conflicting_sources(product1["ram_size"], product2["ram_size"], title_ram(title1), title_ram(title2)):
        return "ram"
    cpu1, cpu2 = exact_cpu(product1), exact_cpu(product2)
    if conflicting(cpu1, cpu2) or cpus_conflict(title_cpu(title1), title_cpu(title2)):
        return "cpu"
    if product_type == "Pc_Bureau_Gamer":
        if cpu1 is None or cpu2 is None:
            return "cpu unknown"  # store-built desktops can only be compared when both name the exact CPU
        # Tunisianet sells DDR4 and DDR5 builds of one desktop under the same headline specs. The laptop ram_type
        # columns are unreliable (GDDR6 read as 'ddr6'), so only desktops compare it
        if conflicting(desktop_ram_type(product1), desktop_ram_type(product2)):
            return "ram type"
        if is_setup(title1) != is_setup(title2):
            return "monitor bundle"
    return None

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
    max_score = 105  # Sum of the points below, so a full match scores 100%
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
        else:
            print("GPU Brand mismatch")
            return 0
    else:
        max_score -= 10
    # The GPU model is compared even when a brand is missing (Tunisianet often leaves it empty)
    if specs1["gpu_model"] != None and specs2["gpu_model"] != None:
        if normalize_gpu(specs1["gpu_model"]) == normalize_gpu(specs2["gpu_model"]):
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
        max_score -= 30  # GPU model and memory unknown
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
    # The brand column is often empty, so the brand named in the title is used first
    brand1, brand2 = laptop_brand(specs1), laptop_brand(specs2)
    if brand1 != None and brand2 != None and fuzz.token_set_ratio(brand1, brand2) > 90:
        score += 10
    else:
        return 0
    if specs1["cpu_brand"] != None and specs2["cpu_brand"] != None:
        if specs1["cpu_brand"] == specs2["cpu_brand"]:
            score += 10
            if specs1["cpu_model"] != None and specs2["cpu_model"] != None and normalize_cpu(specs1["cpu_model"]) == normalize_cpu(specs2["cpu_model"]):
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
            if specs1["gpu_model"] != None and specs2["gpu_model"] != None and normalize_gpu(specs1["gpu_model"]) == normalize_gpu(specs2["gpu_model"]):
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
    # The site compares prices, so the same PC with and without a store-added Windows licence is two different offers
    if windows_bundle(product1) != windows_bundle(product2):
        return 0
    if product1["site_id"] == product2["site_id"]:
        return 999  # Both stores give the same manufacturer reference
    if spec_conflict(product1, product2, product_type):
        return 0

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
        if specs_score == 0:
            return 0
        return (fuzzscore + specs_score) / 2
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

def assign_one_to_one(scored, tie_break=None):
    """Greedy one-to-one assignment over (score, tunisianet_link, store_link) pairs.
    Pairs are taken by score, highest first, and a pair is accepted only if its Tunisianet link and its store link
    are both still free. Equal scores are ordered by tie_break(tunisianet_link, store_link) when given, smallest
    first, then by link, so builds are reproducible. Returns {tunisianet_link: (store_link, score)}."""
    def order(pair):
        score, tunisianet_link, store_link = pair
        extra = tie_break(tunisianet_link, store_link) if tie_break else ()
        return (-score, *extra, tunisianet_link, store_link)

    assigned = {}
    taken = set()
    for score, tunisianet_link, store_link in sorted(scored, key=order):
        if tunisianet_link in assigned or store_link in taken:
            continue
        assigned[tunisianet_link] = (store_link, score)
        taken.add(store_link)
    return assigned

def match_store(tunisianet_products, store_products, product_type):
    """One-to-one matches between Tunisianet and one store, among pairs scoring at least MATCH_THRESHOLD."""
    scored = []
    for product1 in tunisianet_products:
        for product2 in store_products:
            score = similarity_score(product1, product2, product_type)
            if score >= MATCH_THRESHOLD:
                scored.append((score, product1["link"], product2["link"]))
    tunisianet = {product["link"]: product for product in tunisianet_products}
    store = {product["link"]: product for product in store_products}

    def tie_break(tunisianet_link, store_link):
        # Tunisianet often lists one laptop several times (bundles, Windows 11 Pro) under titles that score the same:
        # prefer the listing whose bundle matches the store's, then the closest price
        product1, product2 = tunisianet[tunisianet_link], store[store_link]
        price_gap = abs(product1["price"] - product2["price"]) if product1["price"] is not None and product2["price"] is not None else float("inf")
        return (windows_bundle(product1) != windows_bundle(product2), price_gap)

    return assign_one_to_one(scored, tie_break)

def Create_Table(cursor, query):
    # Create a table in the database
    # Names are lowercased because app.py relies on the lowercase names Postgres used to fold them to
    try:
        cursor.execute(query[1].lower())
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

def main(db_path=DB_PATH):
    # Create a connection to the database built by DB.main
    DB = sqlite3.connect(db_path)
    cursor = DB.cursor()
    # Product Types and Websites
    product_types = ["Pc_Portable_Gamer", "Pc_Bureau_Gamer", "Ecran_Gamer"]
    Websites = ["Tunisianet", "Mytek", "ScoopGaming"]

    for table in Table_Queries:
        Create_Table(cursor, table)
         
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

        # Each store listing is matched to at most one Tunisianet listing, and vice versa
        Mytek_Matches = match_store(Tunisianet_Products, Mytek_Products, product_type)
        ScoopGaming_Matches = match_store(Tunisianet_Products, ScoopGaming_Products, product_type)
        # Every Tunisianet product still gets a row; unmatched stores stay NULL
        for product1 in Tunisianet_Products:
            link = product1['link']
            Insert_Product(cursor, product_type, link, Mytek_Matches.get(link, (None,))[0], ScoopGaming_Matches.get(link, (None,))[0])
        print(f"Total products matched for {product_type}: {len(Mytek_Matches)} with Mytek, {len(ScoopGaming_Matches)} with ScoopGaming")
        Cleaning_Query = "DELETE FROM Matched_" + product_type + " WHERE linkTunisianet NOT IN (SELECT linktunisianet FROM Tunisianet_" + product_type + ");"
        cursor.execute(Cleaning_Query)
    DB.commit()
    print("All products matched and inserted successfully.")

    cursor.close()
    DB.close()
