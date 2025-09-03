# NBA ETL Pipeline

## Description
Pipeline ETL complet pour l'extraction, la transformation et le chargement de données NBA depuis plusieurs sources.

## Fonctionnalités
- ✅ Extraction depuis 5 sources différentes (API, Web scraping, CSV, SQL, Big Data)
- ✅ Transformation et normalisation des données
- ✅ Chargement vers PostgreSQL et MongoDB
- ✅ API REST avec FastAPI
- ✅ Authentification par clé API
- ✅ Conformité RGPD
- ✅ Documentation complète

## Installation

```bash
# Cloner le repository
git clone https://github.com/Yayahajdar/nba.git
cd nba

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

1. Copier `.env.example` vers `.env`
2. Configurer les variables d'environnement :

```env
PUBLIC_API_KEY=nba
BALLDONTLIE_API_KEY=your_api_key_here
MONGODB_URI=mongodb://localhost:27017/nba_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=nba_etl
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
```

## Utilisation

```bash
# Démarrer l'API
uvicorn main:app --reload

# Accéder à la documentation
http://localhost:8000/docs

# Lancer le pipeline ETL
curl -X POST -H "X-API-Key: nba" http://localhost:8000/run-etl
```

## Structure du projet

## Structure du projet

nba_etl/
├── extract_ .py          # Scripts d'extraction
├── transform.py          # Transformation des données
├── load_ .py            # Chargement vers les bases
├── main.py              # API FastAPI
├── models.py            # Modèles de données
├── requirements.txt     # Dépendances
└── data/raw/           # Données extraites


## API Endpoints

- `GET /players` - Liste des joueurs
- `GET /teams` - Liste des équipes
- `GET /games` - Liste des matchs
- `POST /run-etl` - Lancer le pipeline ETL
- `GET /rgpd/info` - Informations RGPD

## Technologies

- **Backend**: Python 3.11+, FastAPI
- **Bases de données**: PostgreSQL, MongoDB
- **Traitement**: Pandas, SQLAlchemy
- **Web scraping**: BeautifulSoup4
- **Documentation**: Markdown



