from fastapi import FastAPI, BackgroundTasks, Depends, Header, HTTPException, status
from sqlalchemy import or_
from dotenv import load_dotenv
import os

from extract_api import run_api
from extract_web import run_web
from extract_csv import run_csv
from extract_sql import run_sql
from extract_big import run_big
from load_pg import load_postgres
from load_mongo import load_mongo
from transform import run_transform
from models import SessionLocal, Player, Team, Game, Season

from fastapi.responses import RedirectResponse

load_dotenv()
PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")

app = FastAPI(title="NBA ETL Runner")

def verify_api_key(x_api_key: str = Header(default=None)):
    # إذا تم ضبط PUBLIC_API_KEY في .env، فعّل التحقق
    if PUBLIC_API_KEY and x_api_key != PUBLIC_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True

# تهيئة قاعدة البيانات عند الإقلاع (إن لزم)
@app.on_event("startup")
def on_startup():
    try:
        from models import init_db
        init_db()
    except Exception as e:
        print(f"⚠️ DB init skipped: {e}")

def full_pipeline():
    players, stats = run_api()
    run_web()
    run_csv()
    run_sql()
    run_big()

    # خطوة التحويل (تطبيع/تنظيف وكتابة ملفات جاهزة)
    run_transform()

    load_postgres(players, stats)
    load_mongo(players, stats)
    print("Full ETL pipeline finished")

# استبدل تعريف POST الأحادي بهذا التعريف متعدد الطرق
@app.api_route("/run-etl", methods=["POST", "GET"])
def trigger(background_tasks: BackgroundTasks, _: bool = Depends(verify_api_key)):
    background_tasks.add_task(full_pipeline)
    return {"status": "ETL started in background"}

# ---- Endpoints القراءة (GET) مع ترقيم وتصفية ----

def player_to_dict(p: Player):
    return {"id": p.id, "first": p.first, "last": p.last, "pos": p.pos, "team_id": p.team_id}

def team_to_dict(t: Team):
    return {"id": t.id, "abbr": t.abbr, "name": t.name}

def game_to_dict(g: Game):
    return {
        "id": g.id, "season": g.season, "date": g.date,
        "home_team_id": g.home_team_id, "visitor_team_id": g.visitor_team_id,
        "home_score": g.home_score, "visitor_score": g.visitor_score
    }

@app.get("/players")
def get_players(team_id: int | None = None, q: str | None = None, page: int = 1, size: int = 20, _: bool = Depends(verify_api_key)):
    with SessionLocal() as sess:
        query = sess.query(Player)
        if team_id is not None:
            query = query.filter(Player.team_id == team_id)
        if q:
            query = query.filter(or_(Player.first.ilike(f"%{q}%"), Player.last.ilike(f"%{q}%")))
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": [player_to_dict(p) for p in items], "page": page, "size": size, "total": total}

@app.get("/teams")
def get_teams(page: int = 1, size: int = 50, _: bool = Depends(verify_api_key)):
    with SessionLocal() as sess:
        query = sess.query(Team)
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": [team_to_dict(t) for t in items], "page": page, "size": size, "total": total}

@app.get("/games")
def get_games(season: int | None = None, team_id: int | None = None, page: int = 1, size: int = 20, _: bool = Depends(verify_api_key)):
    with SessionLocal() as sess:
        query = sess.query(Game)
        if season is not None:
            query = query.filter(Game.season == season)
        if team_id is not None:
            query = query.filter(or_(Game.home_team_id == team_id, Game.visitor_team_id == team_id))
        total = query.count()
        items = query.offset((page - 1) * size).limit(size).all()
        return {"items": [game_to_dict(g) for g in items], "page": page, "size": size, "total": total}

@app.get("/", include_in_schema=False)
def index():
    return RedirectResponse(url="/docs")

@app.get("/health", tags=["meta"], summary="Health check")
def health():
    return {"status": "ok"}



# Ajout dans main.py après les autres endpoints

# Remplacer la section RGPD existante par :

@app.get("/rgpd/info", tags=["RGPD"], summary="Informations de conformité RGPD")
async def info_rgpd():
    """
    Informations sur la conformité RGPD du projet NBA ETL
    """
    return {
        "conformite": "CONFORME",
        "finalite": "Analyse statistique des performances sportives NBA",
        "donnees_traitees": [
            "Statistiques de joueurs (publiques)",
            "Résultats de matchs (publics)",
            "Données historiques (publiques)"
        ],
        "duree_conservation": "Indéfinie pour données historiques, 30 jours pour logs",
        "contact_dpo": os.getenv("RGPD_CONTACT_EMAIL", "dpo@organisation.fr"),
        "derniere_verification": "2024-01-15",
        "mesures_securite": [
            "Authentification par clé API",
            "Chiffrement des communications",
            "Accès restreint aux données"
        ]
    }

@app.get("/rgpd/audit", tags=["RGPD"], summary="Audit de conformité RGPD")
async def audit_rgpd(_: bool = Depends(verify_api_key)):
    """
    Génère et retourne un rapport d'audit RGPD complet (accès restreint)
    """
    import subprocess
    import json
    
    # Exécution du script de vérification
    result = subprocess.run(["python", "rgpd_compliance_check.py"], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        try:
            with open('rapport_rgpd.json', 'r', encoding='utf-8') as f:
                rapport = json.load(f)
            return rapport
        except FileNotFoundError:
            raise HTTPException(status_code=500, detail="Fichier rapport_rgpd.json non trouvé")
    else:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération du rapport: {result.stderr}")

@app.get("/rgpd/privacy-policy", tags=["RGPD"], summary="Politique de confidentialité")
def privacy_policy():
    """
    Retourne la politique de confidentialité du projet
    """
    return {
        "finalite": "Collecte et traitement de données sportives publiques NBA à des fins éducatives et d'analyse",
        "minimisation_donnees": "Seules les données nécessaires au projet sont collectées",
        "mesures_securite": [
            "Authentification API par clés",
            "Chiffrement des connexions base de données",
            "Accès restreint aux données"
        ],
        "partage_donnees": "Aucun partage avec des tiers",
        "traitement_automatise": "Traitement automatisé pour l'agrégation et la normalisation des données",
        "duree_conservation": "Conservation indéfinie justifiée par la finalité d'analyse historique",
        "droits_personnes": "Données publiques - pas d'identification individuelle"
    }

@app.get("/rgpd/report", tags=["RGPD"], summary="Rapport de vérification RGPD")
def get_rgpd_report():
    """
    Récupère le rapport de conformité RGPD généré
    """
    try:
        import json
        with open('rapport_rgpd.json', 'r', encoding='utf-8') as f:
            report = json.load(f)
        return report
    except FileNotFoundError:
        return {"error": "Rapport RGPD non trouvé. Veuillez exécuter rgpd_compliance_check.py d'abord"}

@app.get("/rgpd/report/html", tags=["RGPD"], summary="Rapport RGPD au format HTML")
def get_rgpd_report_html():
    """
    Récupère le rapport de conformité RGPD au format HTML
    """
    try:
        with open('rapport_rgpd.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Rapport HTML non trouvé</h1><p>Veuillez exécuter le script de génération de rapport d'abord.</p>")
