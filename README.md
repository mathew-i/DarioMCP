# DarioMCP

Analny Dariusz - serwer MCP do wykonywania analiz tabel w bazie danych PostgreSQL.

## Opis

DarioMCP to serwer MCP (Model Context Protocol), który analizuje tabele w bazie danych PostgreSQL. Serwer komunikuje się z innym serwerem MCP (Postgres MCP) w celu pobrania metadanych tabel, a następnie wykonuje zaawansowaną analizę, która obejmuje:

- **Określenie typu tabeli** (fact/dimension)
- **Identyfikację kluczy** (primary key, foreign keys, dimension keys)
- **Analizę referencji** (relacje z innymi tabelami)
- **Statystyki rekordów** (liczba rekordów, dzienne obciążenie)

## Wymagania

- Python 3.8+
- uv (szybki instalator pakietów Python) - [Instalacja](https://github.com/astral-sh/uv)
- PostgreSQL database
- Postgres MCP server (opcjonalnie, dla pełnej integracji)

## Instalacja

### Szybka instalacja z uv

```bash
# Zainstaluj uv (jeśli nie masz)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Zainstaluj zależności i projekt (zalecane - automatycznie tworzy .venv)
uv sync

# Lub użyj skryptu instalacyjnego
bash setup/install.sh

# Alternatywnie (jeśli chcesz zainstalować systemowo)
uv pip install -e . --system
```

### Alternatywnie (tradycyjna metoda z pip)

```bash
pip install -r requirements.txt
```

### Konfiguracja zmiennych środowiskowych

```bash
cp .env.example .env
# Edytuj .env i ustaw DATABASE_URI
```

## Uruchomienie

### Jako serwer MCP z uv

```bash
uv run python -m dariomcp.server
```

### Lub tradycyjnie

```bash
python -m dariomcp.server
```

### Konfiguracja dla Claude Desktop

Dodaj do pliku konfiguracyjnego Claude Desktop (zwykle `~/Library/Application Support/Claude/claude_desktop_config.json` na macOS):

**Z uv (zalecane):**

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    }
  }
}
```

**Lub tradycyjnie z Python:**

```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "python",
      "args": ["-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    }
  }
}
```

Lub użyj gotowego pliku `mcp_config.json` jako referencji.

### Konfiguracja dla Cursor IDE

Zobacz szczegółowy przewodnik w pliku `CURSOR_SETUP.md`.

**Szybka konfiguracja** - użyj jednej z opcji:

**Opcja 1: Z uv (jeśli uv jest w PATH)**
```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    }
  }
}
```

**Opcja 2: Z wrapper script (zalecane jeśli uv nie jest w PATH)**
```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "/Users/mateusziwaszkiewicz/repos/myprojects/DarioMCP/DarioMCP/run_server.sh",
      "args": [],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    }
  }
}
```

**Opcja 3: Z Python z venv**
```json
{
  "mcpServers": {
    "dario-mcp": {
      "command": "/Users/mateusziwaszkiewicz/repos/myprojects/DarioMCP/DarioMCP/.venv/bin/python",
      "args": ["-m", "dariomcp.server"],
      "env": {
        "DATABASE_URI": "postgresql://user:password@localhost:5432/dbname"
      }
    }
  }
}
```

**Uwaga**: Zastąp ścieżkę w Opcji 2 i 3 rzeczywistą ścieżką do projektu (użyj `pwd` w katalogu projektu).

## Narzędzia

### analyze_table

Analizuje określoną tabelę w bazie danych.

**Parametry:**
- `schema_name` (wymagane): Nazwa schematu zawierającego tabelę
- `table_name` (wymagane): Nazwa tabeli do analizy
- `database_uri` (opcjonalne): URI połączenia z bazą danych PostgreSQL. Jeśli nie podano, używa zmiennej środowiskowej `DATABASE_URI`
- `postgres_mcp_url` (opcjonalne): URL serwera Postgres MCP (domyślnie: http://localhost:8000)

**Przykład użycia:**

```json
{
  "schema_name": "public",
  "table_name": "sales",
  "database_uri": "postgresql://user:password@localhost:5432/dbname"
}
```

**Wynik analizy:**

Analiza zwraca szczegółowe informacje o tabeli:
- Typ tabeli (fact/dimension)
- Liczba rekordów
- Statystyki dziennego obciążenia
- Klucz główny
- Klucze obce (referencje do innych tabel)
- Klucz wymiaru (dla tabel wymiarów)
- Metadane kolumn, ograniczeń i indeksów

## Architektura

- `dariomcp/server.py` - Główny serwer MCP z definicjami narzędzi
- `dariomcp/table_analyzer.py` - Logika analizy tabel
- `dariomcp/postgres_client.py` - Klient do komunikacji z Postgres MCP (do rozbudowy)

## Rozwój

Projekt jest w fazie rozwoju. Pełna integracja z Postgres MCP przez protokół MCP będzie dostępna w przyszłych wersjach.
