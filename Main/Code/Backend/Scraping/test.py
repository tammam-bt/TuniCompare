from thefuzz import fuzz
import re


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

def similarity_score(title1, title2):
    """
    Calculate the similarity score between two titles.
    """
    # Normalize the titles
    norm_title1 = normalize_string(title1)
    norm_title2 = normalize_string(title2)
    
    # Calculate the similarity score
    score = fuzz.token_set_ratio(norm_title1, norm_title2)
    return score

title1 = "PC Portable Gamer HP Victus 15-fb2000nk AMD RYZEN 5 8Go RTX 2050"
title2 = "Portable Gaming HP Victus Gaming 15-fb2000nk / Ryzen 5 8645HS / RTX 2050 4G / 8 Go DDR5 / 512 Go SSD / Windows 11 / Blanc Avec Antivirus Bitdefender Internet Security / 1 Poste / 1 an"
title3 = "PC Portable ASUS TUF Gaming A15 FA506NF / Ryzen 5 7535HS / RTX 2050 4G / 8 Go / Noir Avec Antivirus Bitdefender Internet Security / 1 Poste / 1 an"

a = title1
b = title3
print()
print("Comparing Titles:")
print("title1:", a)
print(f"Title 1: {normalize_string(a)}")
print("title2:", b)
print(f"Title 2: {normalize_string(b)}")
similarity1 = fuzz.token_set_ratio(a, b)
similarity2 = fuzz.token_set_ratio(normalize_string(a), normalize_string(b))


print(f"Similarity 1: {similarity1}%")
print(f"Similarity 2: {similarity2}%")
