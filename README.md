# AES-256 File Encryptor

Prosta aplikacja napisana w Pythonie umożliwiająca szyfrowanie i deszyfrowanie plików przy użyciu algorytmu **AES-256-GCM**. Program posiada graficzny interfejs użytkownika oparty na bibliotece **CustomTkinter** oraz wykorzystuje **PBKDF2-HMAC-SHA256** do wyprowadzania klucza z hasła.

## Funkcje mojego programu:

- Szyfrowanie dowolnych plików algorytmem AES-256-GCM.
- Deszyfrowanie wcześniej zaszyfrowanych plików.
- Weryfikacja integralności danych dzięki trybowi GCM.
- Automatyczne wykrywanie formatu RAW lub Base64 podczas odszyfrowywania.
- Generowanie losowych haseł kryptograficznych.
- Kopiowanie hasła do schowka.
- Wybór rozszerzenia pliku wyjściowego.
- Obsługa jasnego i ciemnego motywu interfejsu.
- Własny format kontenera przechowujący metadane kryptograficzne.

## Szczególy techniczne

### Kryptografia

- AES-256-GCM
- PBKDF2-HMAC-SHA256
- 300 000 iteracji PBKDF2
- Losowy salt (16 B)
- Losowy nonce (12 B)

### Użyte biblioteki (te ważniejsze):

- CustomTkinter
- Tkinter
- cryptography


## Format pliku zaszyfrowanego

Program zapisuje zaszyfrowane dane w autorskim formacie binarnym zawierającym:

- identyfikator formatu,
- wersję formatu,
- identyfikator KDF,
- identyfikator szyfru,
- liczbę iteracji PBKDF2,
- salt,
- nonce,
- zaszyfrowane dane.

Metadane są uwierzytelniane jako AAD (od ang. *Additional Authenticated Data*), co zabezpiecza je przed modyfikacją.

## Przykładowa instalacja

### 1. Klonowanie repozytorium

```bash
git clone https://github.com/USERNAME/AES_Encryptor_GUI.git
cd AES_Encryptor_GUI
```

### 2. Utworzenie środowiska wirtualnego

#### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalacja zależności

```bash
pip install -r requirements.txt
```

## Uruchamianie

```bash
python -m AES_gui_encryptor
```

lub

```bash
python __main__.py
```

## Jak korzystać z aplikacji?

### Szyfrowanie

1. Wybierz plik wejściowy.
2. Podaj hasło lub wygeneruj je automatycznie.
3. Wybierz lokalizację pliku wynikowego.
4. Opcjonalnie włącz zapis w formacie Base64.
5. Kliknij **Szyfruj**.

### Deszyfrowanie

1. Wybierz zaszyfrowany plik.
2. Podaj poprawne hasło.
3. Wskaż lokalizację pliku wynikowego.
4. Kliknij **Odszyfruj**.

## Bezpieczeństwo

- Program nie przechowuje haseł.
- Dla każdego pliku generowany jest nowy salt i nonce.
- Niepoprawne hasło lub modyfikacja pliku powodują błąd weryfikacji GCM.
- Klucz szyfrujący nigdy nie jest zapisywany na dysku.

## Niektóre ograniczenia

Aktualna wersja programu wczytuje cały plik do pamięci RAM przed szyfrowaniem lub odszyfrowaniem. Rozwiązanie jest wystarczające dla typowych zastosowań edukacyjnych i plików o umiarkowanym rozmiarze.

## Struktura projektu

```text
AES_gui_encryptor/
│   config.py
│   main.py
│   __init__.py
│   __main__.py
│
├── assets/
│   └── app.ico
│
├── presenter/
│   ├── app_presenter.py
│   └── __init__.py
│
├── core/
│   ├── crypto.py
│   ├── encrypted_file_format.py
│   ├── errors.py
│   ├── service.py
│   └── __init__.py
│
├── ui/
│   ├── app.py
│   ├── background.py
│   ├── config.py
│   ├── file_panel.py
│   ├── notes_panel.py
│   ├── output_panel.py
│   ├── password_panel.py
│   ├── sidebar.py
│   ├── styles.py
│   └── __init__.py
│
└── utils/
    ├── password.py
    ├── paths.py
    └── __init__.py
```

## Co można dodać na przyszłość?

- Obsługę bardzo dużych plików w trybie strumieniowym.
- Przeciągnij i upuść (Drag & Drop).
- Integrację z menedżerami haseł.
- Podpisy cyfrowe.
- Obsługę wielu plików jednocześnie.
- Tworzenie gotowych plików wykonywalnych dla systemów Windows, Linux i macOS.

-----

Projekt wykonany w ramach przedmiotu **Projekt Indywidualny** na kierunku **Informatyka Stosowana**.