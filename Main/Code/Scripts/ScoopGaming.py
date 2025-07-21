from bs4 import BeautifulSoup
import requests
import csv
import re
import time

def normalize_text_pc(s):
    # Remove special characters and extra spaces
    s = re.sub(r'[^\w\s",.]', ' ', s) # Remove special characters except for common punctuation
    s = re.sub(r'\s+', ' ', s).strip() # Replace multiple spaces with a single space and strip leading/trailing spaces
    s = re.sub(r'(\d+)([a-zA-Z]+)', lambda m: f"{m.group(1)}{m.group(2)}" if len(m.group(2))==1 else f"{m.group(1)} {m.group(2)}", s)  # Add space between numbers and words (e.g., "16Go" to "16 Go")
    s = s.replace(" ", " ")  # Replace non-breaking spaces with regular spaces
    s = s.lower()  # Convert to lowercase
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
    return s

def normalize_text_ecran(s):
    # Remove special characters and extra spaces
    s = re.sub(r'\s+', ' ', s).strip() # Replace multiple spaces with a single space and strip leading/trailing spaces
    s = re.sub(r'(\d+)([a-zA-Z]+)', lambda m: f"{m.group(1)}{m.group(2)}" if len(m.group(2))==1 else f"{m.group(1)} {m.group(2)}", s)  # Add space between numbers and words (e.g., "16Go" to "16 Go")
    s = s.replace(" ", " ")  # Replace non-breaking spaces with regular spaces
    s = s.lower()  # Convert to lowercase
    s = s.replace("full hd", "fhd")  # Normalize Full HD
    s = s.replace("écran", "ecran")  # Normalize Ecran
    s = s.replace("incurvé", "incurve")  # Normalize Incurvé
    s = s.replace("ecran gaming", "ecran") # Normalize Ecran Gaming
    s = s.replace("ecran gamer", "ecran")  # Normalize Ecran Gamer
    s = s.replace("résolution", "resolution")  # Normalize Résolution
    s = s.replace("luminosité", "luminosite")  # Normalize Luminosité
    s = s.replace("è", "e")  # Normalize è to e
    return s

def get_specs_pc_portablegamer(text):
    # Extract Brand an Model of the laptop
    Stopping_anchor = r'(?:,?\s*(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|connectique|wifi|bluetooth|clavier|ports|$))'
    known_brands = r'(?:msi|asus|dell|gigabyte|acer|lenovo|hp|apple|razer|alienware|samsung|lg|toshiba|sony)'
    Brandmodel_match = re.search(r'(?:pc portable gamer|pc gamer|laptop|ordinateur portable|portable|pc portable|pc)?\s*(' + known_brands + r')\b\s*(.*?)(?:,?\s*(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|$))', text, re.IGNORECASE)
    Brand = Brandmodel_match.group(1) if Brandmodel_match else "Unknown"
    Model = Brandmodel_match.group(2) if Brandmodel_match else "Unknown"
    print(f"Brand: {Brand}")
    print(f"Model: {Model}")
    # Extract CPU
    cpu_match = re.search(r'(?:cpu)\s*(.*?)(?:,?\s*(?:ram|mémoire ram|disque dur|ssd|graphique|nvidia|ecran|$))', text, re.IGNORECASE)
    print(f"CPU Match: {cpu_match.group(1) if cpu_match else 'None'}")
    cpu_description = cpu_match.group(1).strip() if cpu_match else "Unknown"
    if "intel" in cpu_description:
        cpu_brand = "Intel"
        cpu_model = re.search(r'(?:\s*)(i[3579]\s*\d+[a-z])', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:\s*)(i[3579]\s*\d+[a-z])', cpu_description, re.IGNORECASE) else "Unknown"  # Extract Intel CPU model
        cpu_cores = re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE) else "Unknown" # Extract number of cores
        cpu_frequency= re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE) else "Unknown"   # Extract frequency
        cache = re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d)+\s*mb', cpu_description, re.IGNORECASE) else "Unknown"  # Extract cache
    elif "amd" in cpu_description:
        cpu_brand = "AMD"
        cpu_model = re.search(r'(?:\s*)(ryzen\s*\d+\s*?\d+\s*?\w+)', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:\s*)(ryzen\s*\d+\s*?\d+\s*?\w+)', cpu_description, re.IGNORECASE) else "Unknown"  # Extract AMD Ryzen CPU model
        cpu_cores = re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE) else "Unknown"  # Extract number of cores
        cpu_frequency = re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE) else "Unknown"  # Extract frequency
        cache = re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE) else "Unknown"
    else:
        cpu_brand = "Unknown"
        cpu_model = "Unknown"
        cpu_cores = "Unknown"
        cpu_frequency = "Unknown"
        cache = "Unknown"
    print("CPU Brand: " + Brand)
    print("CPU Model: " + cpu_model)
    print("CPU Cores: " + cpu_cores)
    print("CPU Frequency: " + cpu_frequency)
    print("CPU Cache: " + cache)
    #Extract RAM
    ram_size = re.search(r'(?:mémoire ram|ram)\s*(\d+)\s*gb', text, re.IGNORECASE).group(1) if re.search(r'(?:ram|mémoire ram)\s*(\d+)\s*gb', text, re.IGNORECASE) else "Unknown"  # Extract RAM size
    ram_ddr = re.search(r'(ddr\d)', text, re.IGNORECASE).group(1) if re.search(r'(ddr\d)', text, re.IGNORECASE) else "Unknown"  # Extract RAM type
    print(f"Ram Size: {ram_size}")
    print(f"Ram Type: {ram_ddr}")
    # Extract Storage
    storage_match = re.search(r'(?:disque dur|ssd)\s*(.*?)(?:,?\s*(?:gpu|ram|mémoire ram|ecran|connectique|wifi|bluetooth|clavier|ports|$))', text, re.IGNORECASE)
    storage_desc = storage_match.group(1).strip() if storage_match else "Unknown"
    print(f"Storage Match: {storage_desc}")
    storage_size = re.search(r'(?:disque dur|ssd)\s*(\d+)\s*(?:gb|tb)', text, re.IGNORECASE).group(1) if re.search(r'(?:disque dur|ssd)\s*(\d+)\s*(?:gb|tb)', text, re.IGNORECASE) else "Unknown"  # Extract Storage size
    storage_type = re.search(r'(ssd|hdd|nvme)', text, re.IGNORECASE).group(1) if re.search(r'(ssd|hdd|nvme)', text, re.IGNORECASE) else "Unknown" # Extract Storage type
    storage_unit = re.search(r'(gb|tb)', storage_desc, re.IGNORECASE).group(1) if re.search(r'(gb|tb)', storage_desc, re.IGNORECASE) else "Unknown"  # Extract Storage unit
    print(f"Storage Size: {storage_size}")
    print(f"Storage Type: {storage_type}")
    print(f"Storage Unit: {storage_unit}")
    # Extract gpu
    gpu_match = re.search(r'(?:gpu)\s*(.*?)(?:,?\s*(?:ram|disque dur|ssd|ecran|connectique|wifi|$))', text, re.IGNORECASE) 
    print(f"GPU Match: {gpu_match.group(1) if gpu_match else 'None'}")
    gpu_desc = gpu_match.group(1).strip() if gpu_match else "Unknown"
    gpu_brand = re.search(r'(nvidia|amd|intel)', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(nvidia|amd|intel)', gpu_desc, re.IGNORECASE) else "Unknown"  # Extract GPU brand
    gpu_model = re.search(r'(rtx\s*\d+|gtx\s*\d+|radeon\s*\w+)', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(rtx\s*\d+|gtx\s*\d+|radeon\s*\w+)', gpu_desc, re.IGNORECASE) else "Unknown" # Extract GPU model
    gpu_memory = re.search(r'(\d+)\s*gb', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*gb', gpu_desc, re.IGNORECASE) else "Unknown"  # Extract GPU memory
    print(f"GPU Brand: {gpu_brand}")
    print(f"GPU Model: {gpu_model}")
    print(f"GPU Memory: {gpu_memory}")
    # Extract Wi-Fi
    wifi = re.search(r'(?:wifi\s*)(\d+)', text, re.IGNORECASE).group(1) if re.search(r'(?:wifi\s*)(\d+)', text, re.IGNORECASE) else "Unknown"
    
    # Extract Bluetooth
    bluetooth = re.search(r'(?:bluetooth\s*)(\d+)', text, re.IGNORECASE).group(1) if re.search(r'(?:bluetooth\s*)(\d+)', text, re.IGNORECASE) else "Unknown"
    
    # Extract Keyboard
    keyboard = re.search(r'(clavier\s*.*?)(?:,?\s*?(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|connectique|wifi|bluetooth|ports|$))', text, re.IGNORECASE).group(1) if re.search(r'(clavier\s*.*?)(?:,?\s*(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|connectique|wifi|bluetooth|port|$))', text, re.IGNORECASE) else "Unknown"
    
    # Extract Ports
    ports = re.search(r'((connectique|\dx)\s*.*?)(?:,?\s*(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|wifi|bluetooth|clavier|$))', text, re.IGNORECASE).group(1) if re.search(r'(?:connectique|\dx)\s*(.*?)(?:,?\s*(?:cpu|intel|amd|processeur|ram|mémoire ram|disque dur|ssd|gpu|nvidia|ecran|wifi|bluetooth|clavier|$))', text, re.IGNORECASE) else "Unknown"
    print(f"Wi-Fi: {wifi}")
    print(f"Bluetooth: {bluetooth}")
    print(f"Keyboard: {keyboard}")
    print(f"Ports: {ports}")
    # Extract Screen
    screen_match = re.search(r'(?:écran|ecran)\s*(.*?)(?:,?\s*(?:cpu|ram|mémoire ram|disque dur|ssd|graphique|nvidia|connectique|$))', text, re.IGNORECASE).group(1) if re.search(r'(?:écran|ecran)\s*(.*?)(?:,?\s*(?:cpu|ram|mémoire ram|disque dur|ssd|graphique|nvidia|connectique|$))', text, re.IGNORECASE) else "Unknown" # Extract Screen description
    screen_type = re.search(r'(ips|oled|tn|va)', screen_match, re.IGNORECASE).group(1) if re.search(r'(ips|oled|tn|va)', screen_match, re.IGNORECASE) else "Unknown"  # Extract Screen type
    screen_size = re.search(r'(\d+(\.\d+)?)\s*"', screen_match, re.IGNORECASE).group(1) if re.search(r'(\d+(\.\d+)?)\s*"', screen_match, re.IGNORECASE) else "Unknown"
    screen_resolution = re.search(r'(fhd|hd)', screen_match, re.IGNORECASE).group(1) if re.search(r'(fhd|hd)', screen_match, re.IGNORECASE) else "Unknown"  # Extract Screen resolution
    screen_refresh_rate = re.search(r'(\d+)\s*hz', screen_match, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*hz', screen_match, re.IGNORECASE) else "Unknown"  # Extract Screen refresh rate
    print(f"Screen Type: {screen_type}")
    print(f"Screen Size: {screen_size}")
    print(f"Screen Resolution: {screen_resolution}")
    print(f"Screen Refresh Rate: {screen_refresh_rate}")
    return {
        "Brand": Brand,
        "Model": Model,
        "CPU": {
            "Brand": cpu_brand,
            "Model": cpu_model,
            "Cores": cpu_cores,
            "Frequency": cpu_frequency,
            "Cache": cache
        },
        "RAM": {
            "Size": ram_size,
            "Type": ram_ddr
        },
        "Storage": {
            "Size": storage_size,
            "Type": storage_type,
            "Unit": storage_unit,
        },
        "GPU": {
            "Brand": gpu_brand,
            "Model": gpu_model,
            "Memory": gpu_memory
        },
        "Wi-Fi": wifi,
        "Bluetooth": bluetooth,
        "Keyboard": keyboard,
        "Ports": ports,
        "Screen": {
            "Type": screen_type,
            "Size": screen_size,
            "Resolution": screen_resolution,
            "Refresh Rate": screen_refresh_rate
        }
    }

def get_specs_de_bureau_gamer(text):
    # Extract CPU
    cpu_match = re.search(r'(?:cpu)\s*(.*?)(?:,?\s*(?:ram|mémoire ram|disque dur|ssd|graphique|nvidia|ecran|$))', text, re.IGNORECASE)
    print(f"CPU Match: {cpu_match.group(1) if cpu_match else 'None'}")
    cpu_description = cpu_match.group(1).strip() if cpu_match else "Unknown"
    if "intel" in cpu_description:
        cpu_brand = "Intel"
        cpu_model = re.search(r'(?:\s*)(i[3579]-\d+[a-z])', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:\s*)(i[3579]-\d+[a-z])', cpu_description, re.IGNORECASE) else "Unknown"  # Extract Intel CPU model
        cpu_cores = re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE) else "Unknown" # Extract number of cores
        cpu_frequency= re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE) else "Unknown"   # Extract frequency
        cache = re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d)+\s*mb', cpu_description, re.IGNORECASE) else "Unknown"  # Extract cache
    elif "amd" in cpu_match.group(1).strip():
        cpu_brand = "AMD"
        cpu_model = re.search(r'(?:\s*)(ryzen\s*\d+\s*?\d+\s*?\w+)', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:\s*)(ryzen\s*\d+)', cpu_description, re.IGNORECASE) else "Unknown"  # Extract AMD Ryzen CPU model
        cpu_cores = re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*core', cpu_description, re.IGNORECASE) else "Unknown"  # Extract number of cores
        cpu_frequency = re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE).group(1) if re.search(r'(?:up\s*to\s*)(\d+\.\d+|\d+)\s*ghz', cpu_description, re.IGNORECASE) else "Unknown"  # Extract frequency
        cache = re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*mb', cpu_description, re.IGNORECASE) else "Unknown"
    else:
        cpu_brand = "Unknown"
        cpu_model = "Unknown"
        cpu_cores = "Unknown"
        cpu_frequency = "Unknown"
        cache = "Unknown"
    
    #Extract RAM
    ram_size = re.search(r'(?:mémoire ram|ram)\s*(\d+)\s*gb', text, re.IGNORECASE).group(1) if re.search(r'(?:ram|mémoire ram)\s*(\d+)\s*gb', text, re.IGNORECASE) else "Unknown"  # Extract RAM size
    ram_ddr = re.search(r'(ddr\d)', text, re.IGNORECASE).group(1) if re.search(r'(ddr\d)', text, re.IGNORECASE) else "Unknown"  # Extract RAM type
    
    # Extract Storage
    storage_match = re.search(r'(?:disque dur|ssd)\s*(.*?)(?:,?\s*(?:gpu|ram|mémoire ram|ecran|connectique|wifi|bluetooth|clavier|ports|$))', text, re.IGNORECASE)
    storage_desc = storage_match.group(1).strip() if storage_match else "Unknown"
    print(f"Storage Match: {storage_desc}")
    storage_size = re.search(r'(?:disque dur|ssd)\s*(\d+)\s*(?:gb|tb)', text, re.IGNORECASE).group(1) if re.search(r'(?:disque dur|ssd)\s*(\d+)\s*(?:gb|tb)', text, re.IGNORECASE) else "Unknown"  # Extract Storage size
    storage_type = re.search(r'(ssd|hdd|nvme)', text, re.IGNORECASE).group(1) if re.search(r'(ssd|hdd|nvme)', text, re.IGNORECASE) else "Unknown" # Extract Storage type
    storage_unit = re.search(r'(gb|tb)', storage_desc, re.IGNORECASE).group(1) if re.search(r'(gb|tb)', storage_desc, re.IGNORECASE) else "Unknown"  # Extract Storage unit
    
    # Extract gpu
    gpu_match = re.search(r'(?:gpu)\s*(.*?)(?:,?\s*(?:ram|disque dur|ssd|ecran|connectique|wifi|$))', text, re.IGNORECASE) 
    print(f"GPU Match: {gpu_match.group(1) if gpu_match else 'None'}")
    gpu_desc = gpu_match.group(1).strip() if gpu_match else "Unknown"
    gpu_brand = re.search(r'(nvidia|amd|intel)', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(nvidia|amd|intel)', gpu_desc, re.IGNORECASE) else "Unknown"  # Extract GPU brand
    gpu_model = re.search(r'(rtx\s*\d+|gtx\s*\d+|radeon\s*\w+)', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(rtx\s*\d+|gtx\s*\d+|radeon\s*\w+)', gpu_desc, re.IGNORECASE) else "Unknown" # Extract GPU model
    gpu_memory = re.search(r'(\d+)\s*gb', gpu_desc, re.IGNORECASE).group(1) if re.search(r'(\d+)\s*gb', gpu_desc, re.IGNORECASE) else "Unknown"  # Extract GPU memory
    return {
        "CPU": {
            "Brand": cpu_brand,
            "Model": cpu_model,
            "Cores": cpu_cores,
            "Frequency": cpu_frequency,
            "Cache": cache
        },
        "RAM": {
            "Size": ram_size,
            "Type": ram_ddr
        },
        "Storage": {
            "Size": storage_size,
            "Type": storage_type,
            "Unit": storage_unit,
        },
        "GPU": {
            "Brand": gpu_brand,
            "Model": gpu_model,
            "Memory": gpu_memory
        },
    }

def get_specs_ecran(text):
    brand = re.search(r'(?<=ecran\s)(.*?)(?:,)', text)
    Size = re.search(r'(\d{1,2}(\.\d+)?)\s*\"', text)
    resolution = re.search(r'\b(?:fhd|hd|qhd|uhd|(\d{3,4}x\d{3,4}))\b', text)  
    refresh_rate = re.search(r'\d{2,3}\s*hz', text)
    response_time = re.search(r'\d+\s*ms', text)
    contrast = re.search(r'\d+:\d+', text)
    brightness = re.search(r'(?:luminosite:\s*)(.*?)(?:,)', text)
    viewing_angle = re.search(r'\d+°h\s*/\s*\d+°v', text)
    curvature = re.search(r'\d{3,4}r', text)
    connectors = re.findall(r'\b(?:hdmi|displayport|usb type-c|audio)\b', text, re.IGNORECASE)
    audio_ports = re.search(r'ports?\s*audio|sortie de ligne audio|sortie audio', text, re.IGNORECASE)
    flicker_free = re.search(r'sans\s*scintillement', text, re.IGNORECASE)
    blue_light_filter = re.search(r'filtre\s*de\s*lumiere\s*bleu', text, re.IGNORECASE)
    adaptive_sync = re.search(r'synchronisation\s*adaptative', text, re.IGNORECASE)
    panel_type = re.search(r'(\bva\b|\btn\b|\boled\b|\bamoled\b|\bips\b)', text, re.IGNORECASE)
    
    return {
        "Brand" : brand.group(1) if brand else "Unknown Brand",
        "Size": Size.group(1) if Size else "Unknown Size",
        "Resolution": resolution.group(0) if resolution else "Unknown Resolution",
        "Refresh Rate": refresh_rate.group(0) if refresh_rate else "Unknown Refresh Rate",
        "Response Time": response_time.group(0) if response_time else "Unknown Response Time",
        "Contrast": contrast.group(0) if contrast else "Unknown Contrast",
        "Brightness": brightness.group(1) if brightness else "Unknown Brightness",
        "Viewing Angle": viewing_angle.group(0) if viewing_angle else "Unknown Viewing Angle",
        "Curvature": curvature.group(0) if curvature else "Unknown Curvature",
        "Connectors": list(set(connectors)) if connectors else ["Unknown Connectors"],
        "Audio Ports": "Yes" if audio_ports else "No",
        "Flicker Free": "Yes" if flicker_free else "No",
        "Blue Light Filter": "Yes" if blue_light_filter else "No",
        "Adaptive Sync": "Yes" if adaptive_sync else "No",
        "Panel Type": panel_type.group(1) if panel_type else "Unknown Panel Type",
        
    }
    # Extract Screen
    
# Function to fetch product details from a given URL
# and return a list of dictionaries containing product information
def get_product_details_pc_portablegamer(l):        
    i = 0
    product_list = []
    while True:
        i += 1
        try:
            print(f"Fetching page {i}...")
            print(l + str(i))
            time.sleep(1)
            html_text = requests.get(l + str(i)).text
            soup = BeautifulSoup(html_text, "lxml")
            products = soup.find_all("div", class_="thumbnail-container")
            for product in products:
                titlediv = product.find("div", class_="tvproduct-name product-title")
                title = titlediv.find("h6").text.strip()
                print("Title: " + title)
                price = product.find("span", class_="price").text.strip()
                link = product.find("a")["href"]
                image = product.find("img" , class_="tvproduct-hover-img tv-img-responsive")["src"]
                IDdiv = product.find("div", class_="col-sm-12 col-md-2 tvproduct-catalog-price")
                ID= IDdiv.get_text(separator="\n").split("\n")[0].split(":")[1].strip() if IDdiv else "No ID"
                product_html_text = requests.get(link, 'lxml').text
                product_soup = BeautifulSoup(product_html_text, "lxml")
                availability = product.find("div", class_="disponible-category").text.strip().split()[0] if product.find("div", class_="disponible-category") else product.find("div", class_="outofstock-category").text.strip().split()[0] + " " + product.find("div", class_="outofstock-category").text.strip().split()[1]
                Description = product_soup.find("div", class_="tvproduct-page-decs").p.text.strip()
                normalized_description = normalize_text_pc(Description)
                print("Normalized Description: " + normalized_description)
                specs = get_specs_pc_portablegamer(normalized_description)
                print(specs)
                Brand = specs["Brand"]
                Model = specs["Model"]
                cpu_brand = specs["CPU"]["Brand"]
                cpu_model = specs["CPU"]["Model"]
                cpu_cores = specs["CPU"]["Cores"]
                cpu_frequency = specs["CPU"]["Frequency"]
                cache = specs["CPU"]["Cache"]
                ram_size = specs["RAM"]["Size"]
                ram_ddr = specs["RAM"]["Type"]
                storage_size = specs["Storage"]["Size"]
                storage_type = specs["Storage"]["Type"]
                storage_unit = specs["Storage"]["Unit"]
                gpu_brand = specs["GPU"]["Brand"]
                gpu_model = specs["GPU"]["Model"]
                gpu_memory = specs["GPU"]["Memory"]
                wifi = specs["Wi-Fi"]
                bluetooth = specs["Bluetooth"]
                keyboard = specs["Keyboard"]
                ports = specs["Ports"]
                screen_type = specs["Screen"]["Type"]
                screen_size = specs["Screen"]["Size"]
                screen_resolution = specs["Screen"]["Resolution"]
                screen_refresh_rate = specs["Screen"]["Refresh Rate"]
                # Create a dictionary for the product
                productdict = {
                    "title": title,
                    "price": price,
                    "link": link,
                    "image": image,
                    "availability": availability,
                    "ID": ID,
                    "Brand": Brand,
                    "Model": Model,
                    "CPU": {
                        "Brand": cpu_brand,
                        "Model": cpu_model,
                        "Cores": cpu_cores,
                        "Frequency": cpu_frequency,
                        "Cache": cache
                    },
                    "RAM": {
                        "Size": ram_size,
                        "Type": ram_ddr
                    },
                    "Storage": {
                        "Size": storage_size,
                        "Type": storage_type,
                        "Unit": storage_unit,
                    },
                    "GPU": {
                        "Brand": gpu_brand,
                        "Model": gpu_model,
                        "Memory": gpu_memory
                    },
                    "Wi-Fi": wifi,
                    "Bluetooth": bluetooth,
                    "Keyboard": keyboard,
                    "Ports": ports,
                    "Screen": {
                        "Type": screen_type,
                        "Size": screen_size,
                        "Resolution": screen_resolution,
                        "Refresh Rate": screen_refresh_rate
                    }
                }    
                if productdict not in product_list:
                    product_list.append(productdict)
                else:
                    print(f"Duplicate product found: {title} - {price}")    
        except:
            print(f"An error occurred while processing page {i}.")
            pass   
        if products == []:
            print("End of pages reached.")
            break
    print(len(product_list)) 
    print(i)   
    return product_list

def get_product_details_pc_de_bureau_gamer(l):
    i = 0
    product_list = []
    while True:
        i += 1
        try:
            print(f"Fetching page {i}...")
            print(l + str(i))
            time.sleep(1)
            html_text = requests.get(l + str(i)).text
            soup = BeautifulSoup(html_text, "lxml")
            products = soup.find_all("div", class_="thumbnail-container")
            for product in products:
                titlediv = product.find("div", class_="tvproduct-name product-title")
                title = titlediv.find("h6").text.strip()
                price = product.find("span", class_="price").text.strip()
                link = product.find("a")["href"]
                image = product.find("img" , class_="tvproduct-hover-img tv-img-responsive")["src"]
                IDdiv = product.find("div", class_="col-sm-12 col-md-2 tvproduct-catalog-price")
                ID= IDdiv.get_text(separator="\n").split("\n")[0].split(":")[1].strip() if IDdiv else "No ID"
                product_html_text = requests.get(link, 'lxml').text
                product_soup = BeautifulSoup(product_html_text, "lxml")
                availability = product.find("div", class_="disponible-category").text.strip().split()[0] if product.find("div", class_="disponible-category") else product.find("div", class_="outofstock-category").text.strip().split()[0] + " " + product.find("div", class_="outofstock-category").text.strip().split()[1]
                Description = product_soup.find("div", class_="tvproduct-page-decs").p.text.strip()
                normalized_description = normalize_text_pc(Description)
                specs = get_specs_de_bureau_gamer(normalized_description)
                cpu_brand = specs["CPU"]["Brand"]
                cpu_model = specs["CPU"]["Model"]
                cpu_cores = specs["CPU"]["Cores"]
                cpu_frequency = specs["CPU"]["Frequency"]
                cache = specs["CPU"]["Cache"]
                ram_size = specs["RAM"]["Size"]
                ram_ddr = specs["RAM"]["Type"]
                storage_size = specs["Storage"]["Size"]
                storage_type = specs["Storage"]["Type"]
                storage_unit = specs["Storage"]["Unit"]
                gpu_brand = specs["GPU"]["Brand"]
                gpu_model = specs["GPU"]["Model"]
                gpu_memory = specs["GPU"]["Memory"]
                # Create a dictionary for the product
                productdict = {
                    "title": title,
                    "price": price,
                    "link": link,
                    "image": image,
                    "availability": availability,
                    "ID": ID,
                    "CPU": {
                        "Brand": cpu_brand,
                        "Model": cpu_model,
                        "Cores": cpu_cores,
                        "Frequency": cpu_frequency,
                        "Cache": cache
                    },
                    "RAM": {
                        "Size": ram_size,
                        "Type": ram_ddr
                    },
                    "Storage": {
                        "Size": storage_size,
                        "Type": storage_type,
                        "Unit": storage_unit,
                    },
                    "GPU": {
                        "Brand": gpu_brand,
                        "Model": gpu_model,
                        "Memory": gpu_memory
                    }
                }
                if productdict not in product_list:
                    product_list.append(productdict)
                else:
                    print(f"Duplicate product found: {title} - {price}")
        except:
            print(f"An error occurred while processing page {i}.")
            pass   
        if products == []:
            print("End of pages reached.")
            break
    print(len(product_list)) 
    print(i)   
    return product_list    
    
def get_product_details_ecran_gamer(l):
    i = 0    
    product_list = []
    while True:
        i += 1
        try:
            print(f"Fetching page {i}...")
            print(l + str(i))
            time.sleep(1)
            html_text = requests.get(l + str(i)).text
            soup = BeautifulSoup(html_text, "lxml")
            products = soup.find_all("div", class_="thumbnail-container")
            print(len(products))
            for product in products:
                titlediv = product.find("div", class_="tvproduct-name product-title")
                title = titlediv.find("h6").text.strip()
                price = product.find("span", class_="price").text.strip()
                link = product.find("a")["href"]
                image = product.find("img" , class_="tvproduct-defult-img tv-img-responsive")["src"]
                IDdiv = product.find("div", class_="col-sm-12 col-md-2 tvproduct-catalog-price")
                ID= IDdiv.get_text(separator="\n").split("\n")[0].split(":")[1].strip() if IDdiv else "No ID"
                product_html_text = requests.get(link, 'lxml').text
                product_soup = BeautifulSoup(product_html_text, "lxml")
                availability = product.find("div", class_="disponible-category").text.strip().split()[0] if product.find("div", class_="disponible-category") else product.find("div", class_="outofstock-category").text.strip().split()[0] + " " + product.find("div", class_="outofstock-category").text.strip().split()[1]
                Description = product_soup.find("div", class_="tvproduct-page-decs").p.text.strip()
                normalized_description = normalize_text_ecran(Description)
                specs = get_specs_ecran(normalized_description)
                brand = specs["Brand"]
                size = specs["Size"]
                resolution = specs["Resolution"]
                refresh_rate = specs["Refresh Rate"]
                response_time = specs["Response Time"]
                contrast = specs["Contrast"]
                brightness = specs["Brightness"]
                viewing_angle = specs["Viewing Angle"]
                curvature = specs["Curvature"]
                connectors = specs["Connectors"]
                audio_ports = specs["Audio Ports"]
                flicker_free = specs["Flicker Free"]
                blue_light_filter = specs["Blue Light Filter"]
                adaptive_sync = specs["Adaptive Sync"]
                panel_type = specs["Panel Type"]
                # Create a dictionary for the product
                productdict = {
                    "title": title,
                    "price": price,
                    "link": link,
                    "image": image,
                    "availability": availability,
                    "ID": ID,
                    "Brand": brand,
                    "Size": size,
                    "Resolution": resolution,
                    "Refresh Rate": refresh_rate,
                    "Response Time": response_time,
                    "Contrast": contrast,
                    "Brightness": brightness,
                    "Viewing Angle": viewing_angle,
                    "Curvature": curvature,
                    "Connectors": connectors,
                    "Audio Ports": audio_ports,
                    "Flicker Free": flicker_free,
                    "Blue Light Filter": blue_light_filter,
                    "Adaptive Sync": adaptive_sync,
                    "Panel Type": panel_type
                }
                if productdict not in product_list:
                    product_list.append(productdict)
                else:
                    print(f"Duplicate product found: {title} - {price}")
                print(productdict)    
        except:
            print(f"An error occurred while processing page {i}.")
            pass
        if products == []:
            print("End of pages reached.")
            break
    print(len(product_list)) 
    print(i)   
    return product_list
           
#Tunisianet Urls
ScoopGaming = {     "Pc Portable Gamer":"https://www.scoopgaming.com.tn/62-pc-portable-gamer?page=",
                    "Pc de Bureau Gamer" : "https://www.scoopgaming.com.tn/63-pc-de-bureau-gamer?page=",
                    "Ecran Gamer" : "https://www.scoopgaming.com.tn/58-ecrans-gaming?page=",}

# Create a CSV file for each category and write the product details
for item in ScoopGaming:
    with open(f"Main\Products\Scoop Gaming\{item}.csv", "w", newline='', encoding="utf-8") as file:
        if item == "Pc Portable Gamer":
            writer = csv.DictWriter(file, fieldnames=["Title", "Price", "Link", "Image","Availability", "ID",
                                                      "Brand", "Model",
                                                      "CPU Brand", "CPU Model", "CPU Cores", "CPU Frequency", "CPU Cache",
                                                      "RAM Size", "RAM Type",
                                                      "Storage Size","Storage Type","Storage Unit",
                                                      "GPU Brand", "GPU Model", "GPU Memory",
                                                      "Wi-Fi", "Bluetooth", "Keyboard",  "Ports",
                                                      "Screen Type", "Screen Size", "Screen Resolution", "Screen Refresh Rate",
                                                      ])
            writer.writeheader()
            products = get_product_details_pc_portablegamer(ScoopGaming[item])
            for product in products:
                writer.writerow({
                    "Title": product["title"],
                    "Price": product["price"],
                    "Link": product["link"],
                    "Image": product["image"],
                    "Availability": product["availability"],
                    "ID": product["ID"],
                    "Brand": product["Brand"],
                    "Model": product["Model"],
                    "CPU Brand": product["CPU"]["Brand"],
                    "CPU Model": product["CPU"]["Model"],
                    "CPU Cores": product["CPU"]["Cores"],
                    "CPU Frequency": product["CPU"]["Frequency"],
                    "CPU Cache": product["CPU"]["Cache"],
                    "RAM Size": product["RAM"]["Size"],
                    "RAM Type": product["RAM"]["Type"],
                    "Storage Size": product["Storage"]["Size"],
                    "Storage Type": product["Storage"]["Type"],
                    "Storage Unit": product["Storage"]["Unit"],
                    "GPU Brand": product["GPU"]["Brand"],
                    "GPU Model": product["GPU"]["Model"],
                    "GPU Memory": product["GPU"]["Memory"],
                    "Wi-Fi": product["Wi-Fi"],
                    "Bluetooth": product["Bluetooth"],
                    "Keyboard": product["Keyboard"],
                    "Ports": product["Ports"],
                    "Screen Type": product["Screen"]["Type"],
                    "Screen Size": product["Screen"]["Size"],
                    "Screen Resolution": product["Screen"]["Resolution"],
                    "Screen Refresh Rate": product["Screen"]["Refresh Rate"],})
        if item == "Pc de Bureau Gamer":
            writer = csv.DictWriter(file, fieldnames=["Title", "Price", "Link", "Image","Availability", "ID",
                                                      "CPU Brand", "CPU Model", "CPU Cores", "CPU Frequency", "CPU Cache",
                                                      "RAM Size", "RAM Type",
                                                      "Storage Size","Storage Type","Storage Unit",
                                                      "GPU Brand", "GPU Model", "GPU Memory",
                                                      ])
            writer.writeheader()
            products = get_product_details_pc_de_bureau_gamer(ScoopGaming[item])
            for product in products:      
                writer.writerow({
                    "Title": product["title"],
                    "Price": product["price"],
                    "Link": product["link"],
                    "Image": product["image"],
                    "Availability": product["availability"],
                    "ID": product["ID"],
                    "CPU Brand": product["CPU"]["Brand"],
                    "CPU Model": product["CPU"]["Model"],
                    "CPU Cores": product["CPU"]["Cores"],
                    "CPU Frequency": product["CPU"]["Frequency"],
                    "CPU Cache": product["CPU"]["Cache"],
                    "RAM Size": product["RAM"]["Size"],
                    "RAM Type": product["RAM"]["Type"],
                    "Storage Size": product["Storage"]["Size"],
                    "Storage Type": product["Storage"]["Type"],
                    "Storage Unit": product["Storage"]["Unit"],
                    "GPU Brand": product["GPU"]["Brand"],
                    "GPU Model": product["GPU"]["Model"],
                    "GPU Memory": product["GPU"]["Memory"]
                })
        if item == "Ecran Gamer": 
            writer = csv.DictWriter(file, fieldnames=["Title", "Price", "Link", "Image","Availability", "ID",
                                                      "Brand", "Size", "Resolution", "Refresh Rate", "Response Time",
                                                      "Contrast", "Brightness", "Viewing Angle", "Curvature",
                                                      "Connectors", "Audio Ports", "Flicker Free", "Blue Light Filter",
                                                      "Adaptive Sync", "Panel Type",
                                                      ])
            writer.writeheader()  
            products = get_product_details_ecran_gamer(ScoopGaming[item])
            for product in products:
                writer.writerow({
                    "Title": product["title"],
                    "Price": product["price"],
                    "Link": product["link"],
                    "Image": product["image"],
                    "Availability": product["availability"],
                    "ID": product["ID"],
                    "Brand": product["Brand"],
                    "Size": product["Size"],
                    "Resolution": product["Resolution"],
                    "Refresh Rate": product["Refresh Rate"],
                    "Response Time": product["Response Time"],
                    "Contrast": product["Contrast"],
                    "Brightness": product["Brightness"],
                    "Viewing Angle": product["Viewing Angle"],
                    "Curvature": product["Curvature"],
                    "Connectors": product["Connectors"],
                    "Audio Ports": product["Audio Ports"],
                    "Flicker Free": product["Flicker Free"],
                    "Blue Light Filter": product["Blue Light Filter"],
                    "Adaptive Sync": product["Adaptive Sync"],
                    "Panel Type": product["Panel Type"]
                })        
    print(f"Finished writing {item} products to CSV file.")
