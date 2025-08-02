# InterpelBot 🤖

Bot do monitorowania interpelacji i zapytań pisemnych posłów w Sejmie RP z automatycznymi powiadomieniami o nowych odpowiedziach.

## 📋 Opis

InterpelBot to narzędzie Python, które:
- Pobiera interpelacje i zapytania pisemne z oficjalnego API Sejmu RP
- Monitoruje nowe odpowiedzi na interpelacje
- Wysyła powiadomienia o nowych odpowiedziach do kanału Mattermost
- Zapisuje wyniki do pliku JSON dla porównań
- Generuje statystyki dotyczące interpelacji

## 🚀 Funkcjonalności

- **Pobieranie danych**: Automatyczne pobieranie interpelacji i zapytań pisemnych z API Sejmu
- **Monitorowanie zmian**: Porównywanie z poprzednimi wynikami i wykrywanie nowych odpowiedzi
- **Powiadomienia**: Wysyłanie powiadomień do Mattermost o nowych odpowiedziach
- **Statystyki**: Generowanie podsumowań z procentami odpowiedzi i zamkniętych interpelacji
- **Konfiguracja**: Możliwość konfiguracji przez plik konfiguracyjny

## 📦 Wymagania

- Python 3.6+
- Biblioteka `requests`

## 🛠️ Instalacja

### Opcja 1: Instalacja lokalna

1. Sklonuj repozytorium:
```bash
git clone https://github.com/thoranrion/interpelbot.git
cd interpelbot
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

### Opcja 2: Instalacja z Docker (zalecana)

1. Sklonuj repozytorium:
```bash
git clone https://github.com/thoranrion/interpelbot.git
cd interpelbot
```

2. Uruchom skrypt setup:
```bash
chmod +x setup-docker.sh
./setup-docker.sh
```

3. Edytuj konfigurację w pliku `config.json`:
```json
{
  "sejm_term": "10",
  "mattermost_webhook_url": "https://your-mattermost.com/hooks/your-webhook-url",
  "mps": [
    {
      "id": "",
      "mattermost_users": ""
    }
  ]
}
```

4. Uruchom kontener:
```bash
docker-compose up -d
```

5. Sprawdź logi:
```bash
docker-compose logs -f
```

## ⚙️ Konfiguracja

### Plik config.json

Bot używa pliku `config.json` do konfiguracji. Skopiuj plik przykładowy i edytuj go:

```bash
cp config.json.example config.json
```

Przykładowa zawartość:

```json
{
  "sejm_term": "10",
  "mattermost_webhook_url": "https://your-mattermost.com/hooks/your-webhook-url",
  "mps": [
    {
      "id": "1",
      "mattermost_users": "@user1,@user2"
    },
    {
      "id": "2",
      "mattermost_users": "@user3"
    }
  ]
}
```

### Parametry konfiguracji

| Parametr | Opis | Wymagany |
|----------|------|----------|
| `sejm_term` | Numer kadencji Sejmu | Tak |
| `mattermost_webhook_url` | URL webhook Mattermost do wysyłania powiadomień | Tak |
| `mps` | Lista posłów do monitorowania | Tak |
| `mps[].id` | ID posła w systemie Sejmu | Tak |
| `mps[].mattermost_users` | Użytkownicy Mattermost do powiadamiania | Nie |

## 🎯 Użycie

### Uruchomienie lokalne

Uruchom bot komendą:

```bash
python interpelbot.py
```

### Uruchomienie z Docker

Bot uruchamia się automatycznie co godzinę w kontenerze Docker. Możesz również uruchomić go ręcznie:

```bash
# Uruchomienie jednorazowe
docker-compose run --rm interpelbot python interpelbot.py

# Sprawdzenie logów
docker-compose logs -f

# Zatrzymanie kontenera
docker-compose down
```

Bot automatycznie:
1. Pobierze interpelacje z API Sejmu dla wszystkich posłów z konfiguracji
2. Porówna z poprzednimi wynikami
3. Wyśle powiadomienia o nowych odpowiedziach
4. Zapisze wyniki do plików `interpel_{mp_id}.json` (w katalogu skryptu lub `/app/data/` w Docker)

## 📊 Format danych

Bot zapisuje dane w plikach `interpel_{mp_id}.json` w następującym formacie:

```json
[
  {
    "id": "numer_interpelacji",
    "type": "INT|ZAP",
    "title": "Tytuł interpelacji",
    "url": "Link do interpelacji",
    "from": "Autor interpelacji",
    "replies": 2,
    "done": false
  }
]
```

### Pola danych:
- `id` - Numer interpelacji
- `type` - Typ dokumentu (INT = interpelacja, ZAP = zapytanie pisemne)
- `title` - Tytuł interpelacji
- `url` - Link do dokumentu
- `from` - Autor interpelacji
- `replies` - Liczba odpowiedzi (0 = brak odpowiedzi, >0 = ma odpowiedzi)
- `replies_data` - Dane odpowiedzi z API (key, prolongation, lastModified)

## 🔔 Powiadomienia

Bot wysyła powiadomienia do Mattermost w formacie Markdown zawierające:
- Informacje o nowych odpowiedziach
- Tytuły interpelacji
- Liczbę odpowiedzi (poprzednia → aktualna)
- Informację o przedłużeniu terminu odpowiedzi (tylko dla nowych odpowiedzi)
- Linki do dokumentów

## 📈 Statystyki

Po każdym uruchomieniu bot wyświetla podsumowanie:
- Łączna liczba interpelacji
- Liczba interpelacji z odpowiedziami
- Liczba zamkniętych interpelacji
- Procenty odpowiedzi i zamknięć

## 🔧 API Sejmu

Bot korzysta z oficjalnego API Sejmu RP:
- Interpelacje: `https://api.sejm.gov.pl/sejm/term{term}/interpellations`
- Zapytania pisemne: `https://api.sejm.gov.pl/sejm/term{term}/writtenQuestions`

## 🐳 Docker

### Szczegóły techniczne

- **Obraz bazowy**: `python:3.11-alpine` (minimalny rozmiar)
- **Cron**: `dcron` (Alpine's cron daemon)
- **Harmonogram**: Co godzinę (0 * * * *)
- **Logi**: `/var/log/cron.log`
- **Dane**: `/app/data/interpel.json`

### Struktura katalogów

```
interpelbot/
├── data/           # Dane aplikacji (montowane jako volume)
├── logs/           # Logi kontenera (montowane jako volume)
├── docker-compose.yml  # Konfiguracja zmiennych środowiskowych
├── Dockerfile
└── setup-docker.sh
```

### Konfiguracja Docker

Konfiguracja jest przechowywana w pliku `config.json` w kontenerze. Edytuj ten plik przed uruchomieniem kontenera.

## 🐛 Rozwiązywanie problemów

### Brak powiadomień
- Sprawdź czy `mattermost_webhook_url` w `config.json` jest poprawnie ustawione
- Sprawdź połączenie z internetem

### Błędy API
- Sprawdź czy `sejm_term` w `config.json` jest poprawny
- Sprawdź czy ID posłów w `config.json` są poprawne
- Sprawdź dostępność API Sejmu

### Błędy plików
- Sprawdź uprawnienia do zapisu w katalogu
- Sprawdź kodowanie plików (UTF-8)

## 📝 Licencja

Ten projekt jest objęty licencją MIT. Zobacz plik [LICENSE](LICENSE) aby poznać szczegóły.

## 🤝 Wkład

Zachęcamy do kontrybucji! Jeśli chcesz dodać nowe funkcjonalności lub naprawić błędy:

1. Sforkuj repozytorium
2. Utwórz branch dla swojej funkcjonalności (`git checkout -b feature/amazing-feature`)
3. Zcommituj zmiany (`git commit -m 'Add amazing feature'`)
4. Wypushuj do brancha (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

## 📞 Kontakt

**Autor:** Marcin Karwowski  
**GitHub:** [@thoranrion](https://github.com/thoranrion)

Jeśli masz pytania lub sugestie dotyczące projektu, skontaktuj się ze mną przez GitHub. 