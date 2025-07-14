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
- **Konfiguracja**: Możliwość konfiguracji przez zmienne środowiskowe

## 📦 Wymagania

- Python 3.6+
- Biblioteka `requests`

## 🛠️ Instalacja

1. Sklonuj repozytorium:
```bash
git clone <repository-url>
cd interpelbot
```

2. Zainstaluj zależności:
```bash
pip install -r requirements.txt
```

## ⚙️ Konfiguracja

### Plik .env

W katalogu projektu znajduje się przykładowy plik `.env.example`. Możesz go skopiować jako `.env` i uzupełnić własnymi danymi:

```bash
cp .env.example .env
```

Przykładowa zawartość:

```
# Przykładowy plik .env dla InterpelBot
# Skopiuj ten plik jako .env i uzupełnij własnymi danymi

MATTERMOST_WEBHOOK_URL=https://your-mattermost.com/hooks/your-webhook-url
SEJM_TERM=10
MP_ID=484
```

Bot automatycznie załaduje te zmienne środowiskowe przy starcie.

### Zmienne środowiskowe

Bot używa następujących zmiennych środowiskowych (mogą być ustawione w pliku `.env` lub w systemie):

| Zmienna | Opis | Domyślna wartość |
|---------|------|------------------|
| `MATTERMOST_WEBHOOK_URL` | URL webhook Mattermost do wysyłania powiadomień | - |
| `SEJM_TERM` | Numer kadencji Sejmu | `10` |
| `MP_ID` | ID posła do monitorowania | `484` |

### Przykład konfiguracji

```bash
export MATTERMOST_WEBHOOK_URL="https://your-mattermost.com/hooks/your-webhook-url"
export SEJM_TERM="10"
export MP_ID="484"
```

## 🎯 Użycie

Uruchom bot komendą:

```bash
python interpelbot.py
```

Bot automatycznie:
1. Pobierze interpelacje z API Sejmu
2. Porówna z poprzednimi wynikami
3. Wyśle powiadomienia o nowych odpowiedziach
4. Zapisze wyniki do pliku `interpel.json`

## 📊 Format danych

Bot zapisuje dane w pliku `interpel.json` w następującym formacie:

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

## 🐛 Rozwiązywanie problemów

### Brak powiadomień
- Sprawdź czy `MATTERMOST_WEBHOOK_URL` jest poprawnie ustawione
- Sprawdź połączenie z internetem

### Błędy API
- Sprawdź czy `SEJM_TERM` i `MP_ID` są poprawne
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