# load_pg_safe.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from models import SessionLocal, Player, Team, Game, Season

def load_postgres(players, games):
 
    teams = {}
    for p in players:
        team = p.get("team")
        if team and team.get("id") not in teams:
            teams[team["id"]] = {
                "id": team["id"],
                "abbr": team.get("abbreviation", ""),
                "name": team.get("full_name", "")
            }

    for g in games:
        # home team
        ht = g.get("home_team")
        if ht and ht.get("id") not in teams:
            teams[ht["id"]] = {
                "id": ht["id"],
                "abbr": ht.get("abbreviation", ""),
                "name": ht.get("full_name", "")
            }

        # visitor team
        vt = g.get("visitor_team")
        if vt and vt.get("id") not in teams:
            teams[vt["id"]] = {
                "id": vt["id"],
                "abbr": vt.get("abbreviation", ""),
                "name": vt.get("full_name", "")
            }

    # --- تحميل البيانات ---
    with SessionLocal() as sess:
        # تحميل الفرق
        sess.execute(
            pg_insert(Team)
            .values(list(teams.values()))
            .on_conflict_do_nothing()
        )
 
        sess.execute(
            pg_insert(Player)
            .values([
                {
                    "id": p.get("id"),
                    "first": p.get("first_name", ""),
                    "last": p.get("last_name", ""),
                    "pos": p.get("position"),
                    "team_id": p["team"]["id"] if p.get("team") else None
                } for p in players
            ])
            .on_conflict_do_nothing()
        )

       
        sess.execute(
            pg_insert(Season)
            .values([{"year": 2023}])
            .on_conflict_do_nothing()
        )

    
        sess.execute(
            pg_insert(Game)
            .values([
                {
                    "id": g.get("id"),
                    "season": g.get("season"),
                    "date": g.get("date", ""),
                    "home_team_id": g["home_team"]["id"] if g.get("home_team") else None,
                    "visitor_team_id": g["visitor_team"]["id"] if g.get("visitor_team") else None,
                    "home_score": g.get("home_team_score") or 0,
                    "visitor_score": g.get("visitor_team_score") or 0,
                } for g in games
            ])
            .on_conflict_do_nothing()
        )

        
        sess.commit()
        print(f"✅ Loaded {len(players)} players and {len(games)} games into PostgreSQL")
