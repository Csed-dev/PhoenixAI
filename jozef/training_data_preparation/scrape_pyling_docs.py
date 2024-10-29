import requests
from bs4 import BeautifulSoup
import json

def get_code_examples(error_url, error_titel):
    response = requests.get(error_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrahiere problematischen und korrekten Code
    code_blocks = soup.find_all("pre")
    if len(code_blocks) < 2:
        return None  # Sicherstellen, dass es beide Codebeispiele gibt

    # Entferne unnötige Leerzeichen und Zeilenumbrüche
    def clean_code(code):
        lines = code.get_text().strip().splitlines()
        return "\n".join(line.strip() for line in lines)

    problematic_code = clean_code(code_blocks[0])
    correct_code = clean_code(code_blocks[1])

    return {
        "error_titel": error_titel,
        "problematic_code": problematic_code,
        "correct_code": correct_code
    }

def create_training_data():
    BASE_URL = "https://pylint.readthedocs.io/en/stable/user_guide/messages/messages_overview.html"
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extrahiere die Links zu Fehlerseiten und IDs
    messages_overview = soup.find(id="messages-overview")
    error_links = messages_overview.find_all("a", class_="reference internal")[6:] # die ersten 6 Links sind nicht relevant
    
    with open("pylint_training_data.json", "w", encoding="utf-8") as f:
        f.write("[\n")
        first_entry = True  # Flag to manage commas between entries

        for link in error_links:
            href = link.get("href")
            error_url = f"https://pylint.readthedocs.io/en/stable/user_guide/messages/{href}"
            
            # Extrahiere die ID aus dem Text
            link_text = link.get_text()
            error_titel = link_text.split(" / ")[0] # Extrahiere die ID nach dem Slash
            
            code_examples = get_code_examples(error_url, error_titel)
            
            if code_examples:
                if not first_entry:
                    f.write(",\n")  # Füge ein Komma zwischen den Einträgen hinzu
                json.dump(code_examples, f, indent=4)
                first_entry = False
        
        f.write("\n]")  # Schließe das JSON-Array
    print("Training data saved to pylint_training_data.json")

create_training_data()
