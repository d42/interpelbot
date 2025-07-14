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

def get_mattermost_webhook_url():
    """Get Mattermost webhook URL from environment variable"""
    return os.getenv('MATTERMOST_WEBHOOK_URL')

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

def load_previous_results(filename="interpel.json"):
    """Load previous results from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    except Exception as e:
        print(f"⚠️  Błąd podczas wczytywania poprzednich wyników: {e}")
        return []

def compare_and_notify_new_answers(current_results, previous_results):
    """Compare current and previous results and send notifications about new answers"""
    if not previous_results:
        print("📝 Pierwsze uruchomienie - brak poprzednich wyników do porównania")
        return
    
    print(f"🔍 Porównuję z poprzednimi wynikami...")
    
    # Create dictionary for quick lookup
    previous_dict = {item['id']: item for item in previous_results if item.get('id')}
    
    new_answers = []
    
    for current_item in current_results:
        current_id = current_item.get('id')
        if not current_id:
            continue
        
        # Skip if current item is marked as done
        if current_item.get('done', False):
            print(f"  ⏭️  Pomijam zakończoną interpelację {current_id}")
            continue
            
        previous_item = previous_dict.get(current_id)
        
        if previous_item:
            # Skip if previous item was also marked as done
            if previous_item.get('done', False):
                print(f"  ⏭️  Pomijam wcześniej zakończoną interpelację {current_id}")
                continue
                
            previous_replies = previous_item.get('replies', 0)
            current_replies = current_item.get('replies', 0)
            
            if current_replies > previous_replies:
                new_count = current_replies - previous_replies
                new_answers.append({
                    'id': current_id,
                    'type': current_item.get('type'),
                    'title': current_item.get('title'),
                    'url': current_item.get('url'),
                    'previous_replies': previous_replies,
                    'current_replies': current_replies,
                    'new_count': new_count
                })
        else:
            # New interpellation with answers (but not done)
            current_replies = current_item.get('replies', 0)
            if current_replies > 0 and not current_item.get('done', False):
                new_answers.append({
                    'id': current_id,
                    'type': current_item.get('type'),
                    'title': current_item.get('title'),
                    'url': current_item.get('url'),
                    'previous_replies': 0,
                    'current_replies': current_replies,
                    'new_count': current_replies
                })
    
    # Send notifications if there are new answers
    if new_answers:
        print(f"🎉 Znaleziono {len(new_answers)} interpelacji z nowymi odpowiedziami!")
        
        # Prepare notification message
        message = "## 🆕 Nowe odpowiedzi na interpelacje!\n\n"
        
        for answer in new_answers:
            message += f"### {answer['type']} ({answer['id']})\n"
            message += f"**{answer['title']}**\n"
            message += f"Odpowiedzi: {answer['previous_replies']} → {answer['current_replies']} (+{answer['new_count']})\n"
            message += f"🔗 [{answer['url']}]({answer['url']})\n\n"
        
        # Send to Mattermost
        send_mattermost_notification(message)
    else:
        print("📭 Brak nowych odpowiedzi")



def save_results_to_json(results, filename="interpel.json"):
    """Save search results to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Count answers and closed interpellations
    answered_count = sum(1 for item in results if item.get('replies', 0) > 0)
    closed_count = sum(1 for item in results if item.get('done', False))
    total_count = len(results)
    
    print(f"\n" + "="*60)
    print(f"PODSUMOWANIE WYNIKÓW")
    print(f"="*60)
    print(f"Wyniki zapisano do pliku: {filename}")
    print(f"Łączna liczba interpelacji: {total_count}")
    print(f"Interpelacje z odpowiedziami: {answered_count}")
    print(f"Interpelacje bez odpowiedzi: {total_count - answered_count}")
    print(f"Zamknięte interpelacje: {closed_count}")
    
    if total_count > 0:
        answered_percentage = (answered_count / total_count) * 100
        closed_percentage = (closed_count / total_count) * 100
        print(f"Procent interpelacji z odpowiedziami: {answered_percentage:.1f}%")
        print(f"Procent zamkniętych interpelacji: {closed_percentage:.1f}%")
    
    print(f"="*60)
    return filename

def get_sejm_term_from_env():
    """Get Sejm term from environment variable or use default"""
    env_term = os.getenv('SEJM_TERM')
    if env_term:
        return env_term
    else:
        return "10"  # Default term

def get_mp_id_from_env():
    """Get MP ID from environment variable or use default"""
    env_mp_id = os.getenv('MP_ID')
    if env_mp_id:
        return env_mp_id
    else:
        return "484"  # Default MP ID

def fetch_interpellations_from_api():
    """Fetch interpellations from Sejm API for the specified MP"""
    try:
        term = get_sejm_term_from_env()
        mp_id = get_mp_id_from_env()
        
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
        
        # Count replies and check if any has prolongation: false
        replies = item.get('replies', [])
        replies_count = len(replies) if isinstance(replies, list) else 0
        
        is_done = False
        if isinstance(replies, list):
            for reply in replies:
                if isinstance(reply, dict) and reply.get('prolongation') == False:
                    is_done = True
                    break
        
        return {
            'id': str(interpellation_id),
            'type': item_type,
            'title': title,
            'url': url,
            'from': from_field,
            'replies': replies_count,
            'done': is_done
        }
        
    except Exception as e:
        print(f"  ⚠️  Błąd podczas przetwarzania elementu API: {e}")
        return None

def main():
    """Main function to run the interpellation search"""
    # Load previous results for comparison
    previous_results = load_previous_results()
    
    print("Pobieranie interpelacji z API Sejmu...")
    interpellations = fetch_interpellations_from_api()
    
    if not interpellations:
        print("Nie udało się pobrać interpelacji z API.")
        return
    
    print(f"Znaleziono {len(interpellations)} interpelacji w API.")
    
    # Zapisz wszystkie interpelacje bez filtrowania po nazwiskach
    save_results_to_json(interpellations)
    
    # Porównaj z poprzednimi wynikami i wyślij powiadomienia
    compare_and_notify_new_answers(interpellations, previous_results)

if __name__ == "__main__":
    main()
