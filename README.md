# Parallel Downloader (Python asyncio + Docker)

## Opis projektu
Projekt implementuje aplikację w języku Python umożliwiającą równoległe pobieranie wielu plików z internetu. Rozwiązanie wykorzystuje programowanie współbieżne oparte o bibliotekę `asyncio`, co pozwala znacząco skrócić czas realizacji operacji sieciowych w porównaniu do podejścia sekwencyjnego.

Aplikacja została przygotowana do uruchamiania w kontenerze Docker, co zapewnia przenośność oraz powtarzalność środowiska uruchomieniowego.

---

## Cel projektu
Celem projektu jest:
- wykorzystanie mechanizmów programowania współbieżnego w Pythonie,
- przyspieszenie operacji typu I/O-bound,
- porównanie trybu sekwencyjnego i równoległego,
- zaprezentowanie uruchomienia aplikacji w środowisku kontenerowym.

---

## Technologie
- Python 3.11
- asyncio
- aiohttp
- tqdm
- Docker

---

## Struktura projektu
parallel-downloader/
├── cli.py
├── downloader.py
├── urls.txt
├── requirements.txt
├── Dockerfile
└── README.md


---

## Plik z adresami URL
Adresy plików do pobrania należy umieścić w pliku `urls.txt`, po jednym adresie w każdej linii. Linie zaczynające się od znaku `#` są ignorowane.

Przykład:
```txt
https://speedtest.orange.pl/files/10MB.bin
https://speedtest.orange.pl/files/100MB.bin
https://ftp.icm.edu.pl/pub/Linux/ubuntu-releases/22.04/ubuntu-22.04.3-live-server-amd64.iso
```

## Uruchomienie lokalne

### Wymagania
Python 3.10 lub nowszy
pip

### Instalacja zależności
``` txt
pip install -r requirements.txt
```

### Uruchomienie równoległe
``` txt
python cli.py --urls urls.txt --out downloads --concurrency 8
```

### Uruchomienie sekwencyjne
``` txt
python cli.py --urls urls.txt --out downloads --sequential
```

## Uruchomienie w Dockerze
### Budowa obrazu
```txt
docker build -t parallel-downloader .
Uruchomienie (Linux / macOS)
docker run --rm \
  -v "$(pwd)/downloads:/app/downloads" \
  -v "$(pwd)/urls.txt:/app/urls.txt" \
  parallel-downloader \
  python cli.py --urls /app/urls.txt --out downloads --concurrency 8
```

## Uruchomienie (Windows PowerShell)
```txt
docker run --rm `
  -v "${PWD}\downloads:/app/downloads" `
  -v "${PWD}\urls.txt:/app/urls.txt" `
  parallel-downloader `
  python cli.py --urls /app/urls.txt --out downloads --concurrency 8
```

## Uruchomienie (Windows Git Bash)
```txt
MSYS_NO_PATHCONV=1 docker run --rm \
  -v "$(pwd -W)/downloads:/app/downloads" \
  -v "$(pwd -W)/urls.txt:/app/urls.txt" \
  parallel-downloader \
  python cli.py --urls /app/urls.txt --out downloads --concurrency 8
```
### Pobrane pliki zapisywane są w katalogu downloads na komputerze hosta.

---

## Parametry programu
```txt --urls ``` – ścieżka do pliku z adresami URL
- ``` txt --out ``` – katalog docelowy
- ``` txt --concurrency ``` – maksymalna liczba jednoczesnych pobrań
- ``` txt --retries ``` – liczba ponowień w przypadku błędów
- ``` txt --timeout ``` – timeout żądania
- ``` txt --sequential ``` – tryb sekwencyjny

## Uwagi
Niektóre publiczne serwery mogą ograniczać dostęp z kontenerów Docker. W testach zaleca się korzystanie z serwerów zapewniających stabilne połączenie.
