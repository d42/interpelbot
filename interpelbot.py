import requests
from datetime import datetime
import os
import json

# Dodane: ładowanie zmiennych środowiskowych z pliku .env jeśli istnieje
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_data_file_path(mp_id):
    """Get absolute path to the data file for specific MP"""
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if we're running in Docker (data directory mounted)
    docker_data_path = f"/app/data/interpel_{mp_id}.json"
    if os.path.exists(docker_data_path):
        return docker_data_path
    
    # Otherwise use the script directory
    return os.path.join(script_dir, f"interpel_{mp_id}.json")

def get_mattermost_webhook_url():
    """Get Mattermost webhook URL from config or environment variable"""
    # Try to get from config first
    config = load_config()
    if config and config.get('mattermost_webhook_url'):
        return config.get('mattermost_webhook_url')
    
    # Fallback to environment variable
    return os.getenv('MATTERMOST_WEBHOOK_URL')

def load_config():
    """Load configuration from JSON file"""
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Błąd podczas wczytywania konfiguracji: {e}")
        return None

def send_mattermost_notification(message, webhook_url=None):
    """Send notification to Mattermost channel"""
    if not webhook_url:
        webhook_url = get_mattermost_webhook_url()
    
    if not webhook_url:
        print("⚠️  Brak URL webhook Mattermost - pomijam powiadomienie")
        return False
    
    try:
        payload = {
            "text": message,
            "username": "InterpelBot",
            "icon_emoji": ":parliament:"
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Powiadomienie wysłane do Mattermost")
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas wysyłania powiadomienia: {e}")
        return False

def load_previous_results(mp_id):
    """Load previous results from JSON file for specific MP"""
    filename = get_data_file_path(mp_id)
    print(f"🔍 Sprawdzam plik dla posła {mp_id}: {filename}")
    try:
        if os.path.exists(filename):
            print(f"✅ Plik istnieje, wczytuję dane...")
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"📊 Wczytano {len(data)} interpelacji z pliku")
                return data
        else:
            print(f"❌ Plik nie istnieje: {filename}")
        return []
    except Exception as e:
        print(f"⚠️  Błąd podczas wczytywania poprzednich wyników: {e}")
        return []

def compare_and_notify_new_answers(current_results, previous_results, mp_id):
    """Compare current and previous results and send notifications about new answers"""
    if not previous_results:
        print("📝 Pierwsze uruchomienie - brak poprzednich wyników do porównania")
        print("📭 Brak nowych odpowiedzi")
        return
    
    print(f"🔍 Porównuję z poprzednimi wynikami dla posła {mp_id}...")
    
    # Get Mattermost users from config for this MP
    config = load_config()
    mattermost_users = ""
    if config:
        for mp_config in config.get('mps', []):
            if mp_config.get('id') == mp_id:
                mattermost_users = mp_config.get('mattermost_users', '')
                break
    
    # Create dictionary for quick lookup (use both id and type as key)
    previous_dict = {}
    for item in previous_results:
        if item.get('id'):
            key = f"{item['id']}_{item.get('type', '')}"
            previous_dict[key] = item
    
    new_answers = []
    
    for current_item in current_results:
        current_id = current_item.get('id')
        current_type = current_item.get('type', '')
        if not current_id:
            continue
            
        # Create key using both id and type
        current_key = f"{current_id}_{current_type}"
        previous_item = previous_dict.get(current_key)
        
        if previous_item:
            previous_replies = previous_item.get('replies', 0)
            current_replies = current_item.get('replies', 0)
            
            if current_replies > previous_replies:
                new_count = current_replies - previous_replies
                
                # Check if any of the new replies has prolongation: true
                has_prolongation = False
                current_replies_data = current_item.get('replies_data', [])
                if isinstance(current_replies_data, list) and len(current_replies_data) > previous_replies:
                    # Check only the newest replies (those beyond the previous count)
                    new_replies = current_replies_data[previous_replies:]
                    for reply in new_replies:
                        if isinstance(reply, dict) and reply.get('prolongation') == True:
                            has_prolongation = True
                            break
                
                # Convert MP IDs to names only for interpelations with new answers
                from_field = current_item.get('from', '')
                term = get_sejm_term_from_env()
                from_field_names = convert_mp_ids_to_names(from_field, term)
                
                new_answers.append({
                    'id': current_id,
                    'type': current_item.get('type'),
                    'title': current_item.get('title'),
                    'url': current_item.get('url'),
                    'from': from_field_names,  # Use converted names
                    'previous_replies': previous_replies,
                    'current_replies': current_replies,
                    'new_count': new_count,
                    'has_prolongation': has_prolongation
                })
        else:
            # New interpellation with answers
            current_replies = current_item.get('replies', 0)
            if current_replies > 0:
                # Check if any of the replies has prolongation: true
                has_prolongation = False
                current_replies_data = current_item.get('replies_data', [])
                if isinstance(current_replies_data, list):
                    for reply in current_replies_data:
                        if isinstance(reply, dict) and reply.get('prolongation') == True:
                            has_prolongation = True
                            break
                
                # Convert MP IDs to names only for interpelations with new answers
                from_field = current_item.get('from', '')
                term = get_sejm_term_from_env()
                from_field_names = convert_mp_ids_to_names(from_field, term)
                
                new_answers.append({
                    'id': current_id,
                    'type': current_item.get('type'),
                    'title': current_item.get('title'),
                    'url': current_item.get('url'),
                    'from': from_field_names,  # Use converted names
                    'previous_replies': 0,
                    'current_replies': current_replies,
                    'new_count': current_replies,
                    'has_prolongation': has_prolongation
                })
    
    # Send notifications if there are new answers
    if new_answers:
        print(f"🎉 Znaleziono {len(new_answers)} interpelacji z nowymi odpowiedziami!")
        
        # Log IDs of interpelations with new answers
        answer_ids = [answer['id'] for answer in new_answers]
        print(f"📋 ID interpelacji z nowymi odpowiedziami: {', '.join(answer_ids)}")
        
        # Prepare notification message
        message = "## 🆕 Nowe odpowiedzi na interpelacje!\n\n"
        
        for answer in new_answers:
            message += f"#### {answer['title']} {answer['type']} ({answer['id']})\n"
            
            # Add information about MPs who submitted the interpellation
            from_field = answer.get('from', '')
            if from_field:
                message += f"**Wnioskujący:** {from_field}\n"
            
            message += f"Odpowiedzi: {answer['previous_replies']} → {answer['current_replies']} (+{answer['new_count']})\n"
            
            # Add prolongation information if available
            if answer.get('has_prolongation', False):
                message += f"⏰ **Przedłużenie terminu odpowiedzi**\n"
            
            # Extract href from URL object or use URL directly if it's a string
            url_display = answer['url']['href'] if isinstance(answer['url'], dict) and 'href' in answer['url'] else answer['url']
            message += f"{url_display}\n\n--------------------------------\n\n"
        
        # Add users mention at the end if configured
        if mattermost_users:
            message += f"\n\n{mattermost_users}"
        
        # Add extra line break at the end for better visibility in Mattermost
        message += "\n"
        
        # Send to Mattermost
        send_mattermost_notification(message)
    else:
        print("📭 Brak nowych odpowiedzi")

def save_results_to_json(results, mp_id):
    """Save search results to JSON file for specific MP"""
    filename = get_data_file_path(mp_id)
    
    # Ensure the directory exists (for Docker data directory)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Count answers
    answered_count = sum(1 for item in results if item.get('replies', 0) > 0)
    total_count = len(results)
    
    print(f"\n" + "="*60)
    print(f"PODSUMOWANIE WYNIKÓW DLA POSŁA {mp_id}")
    print(f"="*60)
    print(f"Wyniki zapisano do pliku: {filename}")
    print(f"Łączna liczba interpelacji: {total_count}")
    print(f"Interpelacje z odpowiedziami: {answered_count}")
    print(f"Interpelacje bez odpowiedzi: {total_count - answered_count}")
    
    if total_count > 0:
        answered_percentage = (answered_count / total_count) * 100
        print(f"Procent interpelacji z odpowiedziami: {answered_percentage:.1f}%")
    
    print(f"="*60)
    return filename





def process_single_mp(mp_id, term):
    """Process interpelations for a single MP"""
    print(f"\n{'='*60}")
    print(f"PRZETWARZANIE POSŁA {mp_id}")
    print(f"{'='*60}")
    
    # Load previous results for comparison
    previous_results = load_previous_results(mp_id)
    
    print(f"Pobieranie interpelacji dla posła {mp_id} z API Sejmu...")
    interpellations = fetch_interpellations_from_api(mp_id, term)
    
    if not interpellations:
        print(f"Nie udało się pobrać interpelacji dla posła {mp_id} z API.")
        return
    
    print(f"Znaleziono {len(interpellations)} interpelacji dla posła {mp_id} w API.")
    
    # Porównaj z poprzednimi wynikami i wyślij powiadomienia
    compare_and_notify_new_answers(interpellations, previous_results, mp_id)
    
    # Zapisz wszystkie interpelacje po porównaniu
    save_results_to_json(interpellations, mp_id)

def fetch_mp_data(mp_id, term="10"):
    """Fetch MP data from Sejm API"""
    try:
        url = f"https://api.sejm.gov.pl/sejm/term{term}/MP/{mp_id}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.205 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        mp_data = response.json()
        return {
            'id': mp_data.get('id'),
            'name': mp_data.get('firstLastName', ''),
            'club': mp_data.get('club', '')
        }
        
    except Exception as e:
        print(f"⚠️  Błąd podczas pobierania danych posła {mp_id}: {e}")
        return {'id': mp_id, 'name': f'Poseł {mp_id}', 'club': ''}

def convert_mp_ids_to_names(from_field, term="10"):
    """Convert MP IDs to names using Sejm API"""
    if not from_field:
        return ""
    
    # Split by comma and clean up
    mp_ids = [mp_id.strip() for mp_id in from_field.split(',') if mp_id.strip()]
    
    mp_names = []
    for mp_id in mp_ids:
        mp_data = fetch_mp_data(mp_id, term)
        mp_names.append(mp_data['name'])
    
    return ", ".join(mp_names)

def fetch_interpellations_from_api(mp_id, term):
    """Fetch interpellations from Sejm API for the specified MP"""
    try:
        print(f"🔍 Pobieranie interpelacji dla posła ID: {mp_id} z kadencji: {term}")
        
        # Fetch both types of interpellations
        interpellations = []
        
        # Fetch regular interpellations
        int_url = f"https://api.sejm.gov.pl/sejm/term{term}/interpellations?limit=500&sort_by=num&from={mp_id}"
        print(f"📋 Pobieranie interpelacji z: {int_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.205 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'pl-PL,pl;q=0.9,en;q=0.8'
        }
        
        response = requests.get(int_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        int_data = response.json()
        if isinstance(int_data, list):
            for item in int_data:
                processed_item = process_api_item(item, "INT")
                if processed_item:
                    interpellations.append(processed_item)
        
        # Fetch written questions
        zap_url = f"https://api.sejm.gov.pl/sejm/term{term}/writtenQuestions?limit=500&sort_by=num&from={mp_id}"
        print(f"📋 Pobieranie zapytań pisemnych z: {zap_url}")
        
        response = requests.get(zap_url, headers=headers, timeout=30)
        response.raise_for_status()
        
        zap_data = response.json()
        if isinstance(zap_data, list):
            for item in zap_data:
                processed_item = process_api_item(item, "ZAP")
                if processed_item:
                    interpellations.append(processed_item)
        
        print(f"✅ Pobrano {len(interpellations)} interpelacji z API")
        return interpellations
        
    except requests.RequestException as e:
        print(f"❌ Błąd podczas pobierania z API: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ Błąd podczas parsowania JSON z API: {e}")
        return []
    except Exception as e:
        print(f"❌ Nieoczekiwany błąd API: {e}")
        return []

def process_api_item(item, item_type):
    """Process a single API item and extract required fields"""
    try:
        # Extract required fields
        links = item.get('links', [])
        url = links[0] if links else ""
        
        interpellation_id = item.get('num', "")
        title = item.get('title', "")
        from_field = item.get('from', "")
        
        # Handle from field - it might be a list or string
        if isinstance(from_field, list):
            from_field = ", ".join(from_field) if from_field else ""
        elif not isinstance(from_field, str):
            from_field = str(from_field) if from_field else ""
        
        # Count replies
        replies = item.get('replies', [])
        replies_count = len(replies) if isinstance(replies, list) else 0
        
        # Filter replies to keep only key, prolongation, lastModified
        filtered_replies = []
        if isinstance(replies, list):
            for reply in replies:
                if isinstance(reply, dict):
                    filtered_reply = {
                        'key': reply.get('key', ''),
                        'prolongation': reply.get('prolongation', False),
                        'lastModified': reply.get('lastModified', '')
                    }
                    filtered_replies.append(filtered_reply)
        
        return {
            'id': str(interpellation_id),
            'type': item_type,
            'title': title,
            'url': url,
            'from': from_field,  # Keep original IDs for now
            'replies': replies_count,
            'replies_data': filtered_replies
        }
        
    except Exception as e:
        print(f"  ⚠️  Błąd podczas przetwarzania elementu API: {e}")
        return None

def main():
    """Main function to run the interpellation search for multiple MPs"""
    # Load configuration
    config = load_config()
    if not config:
        print("❌ Nie udało się wczytać konfiguracji.")
        print("📝 Utwórz plik config.json z konfiguracją posłów.")
        return
    
    # Get term from config
    term = config.get('sejm_term', '10')
    mps = config.get('mps', [])
    
    if not mps:
        print("❌ Brak posłów w konfiguracji")
        return
    
    print(f"📋 Znaleziono {len(mps)} posłów w konfiguracji")
    
    # Process each MP
    for mp_config in mps:
        mp_id = mp_config.get('id')
        
        if not mp_id:
            print("⚠️  Pomijam posła bez ID")
            continue
        
        try:
            process_single_mp(mp_id, term)
        except Exception as e:
            print(f"❌ Błąd podczas przetwarzania posła {mp_id}: {e}")
            continue
    
    print(f"\n✅ Zakończono przetwarzanie wszystkich {len(mps)} posłów")

if __name__ == "__main__":
    main()
