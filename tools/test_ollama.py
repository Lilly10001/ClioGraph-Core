import requests
import json

def test_translation():
    # 1. Lokale URL deines Ollama-Dienstes
    url = "http://localhost:11434/api/generate"
    
    # 2. Präziser Prompt für die Übersetzung
    prompt = "Translate the German word 'Guten Tag' to Italian. Reply ONLY with the direct translation, nothing else."
    
    # 3. Payload-Struktur (Wir nutzen llama3 als Basismodell)
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False  # Wichtig: Verhindert, dass die KI wortweise streamt
    }
    
    print("⏳ Sende Anfrage an den lokalen Ollama-Server... Bitte warten.")
    
    try:
        # Wir geben dem lokalen PC 15 Sekunden Zeit zum Antworten
        response = requests.post(url, json=payload, timeout=15.0)
        
        if response.status_code == 200:
            result_json = response.json()
            translation = result_json.get("response", "").strip()
            print("\n✅ VERBINDUNG ERFOLGREICH!")
            print(f"Original (DE): 'Guten Tag'")
            print(f"Ollama (IT):   '{translation}'")
        else:
            print(f"\n❌ FEHLER: Server antwortet mit Status-Code {response.status_code}")
            print(response.text)
            
    except requests.exceptions.ConnectionError:
        print("\n❌ VERBINDUNG FEHLGESCHLAGEN!")
        print("Der Ollama-Dienst läuft anscheinend nicht im Hintergrund.")
        print("Bitte öffne ein Windows-Terminal (cmd) und starte den Dienst mit: ollama run llama3")
    except Exception as e:
        print(f"\n❌ UNERWARTETER FEHLER: {str(e)}")

if __name__ == "__main__":
    test_translation()
