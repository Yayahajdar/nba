#!/usr/bin/env python3
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    try:
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL non définie dans .env")
            return False
            
        print(f"🔍 Test de connexion à : {database_url.split('@')[1] if '@' in database_url else database_url}")
        
        engine = create_engine(database_url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version();"))
            version = result.fetchone()[0]
            print(f"✅ Connexion réussie !")
            print(f"📊 Version PostgreSQL : {version}")
            return True
            
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("\n💡 Vérifiez :")
        print("   - PostgreSQL est démarré")
        print("   - Les informations dans .env sont correctes")
        print("   - L'utilisateur et la base de données existent")
        return False

if __name__ == "__main__":
    test_database_connection()