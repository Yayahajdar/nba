import pandas as pd
import json
from pymongo import MongoClient, UpdateOne, errors
from dotenv import load_dotenv
import os

 
load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI/MONGODB_URI not found in .env file")

client = MongoClient(MONGO_URI)
mdb = client["nba"]

def player_to_dict(p):
    if isinstance(p, dict):
        d = p.copy()   
    else:
        d = p.__dict__.copy()   

     
    if "team" in d and not isinstance(d["team"], dict):
        if hasattr(d["team"], "__dict__"):
            d["team"] = d["team"].__dict__

    return d

def stat_to_dict(s):
    return s.__dict__ if hasattr(s, "__dict__") else s

def deduplicate_collection(coll, key: str = "id"):
 
    pipeline = [
        {"$match": {key: {"$ne": None}}},
        {"$group": {"_id": f"${key}", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
        {"$match": {"count": {"$gt": 1}}}
    ]
    duplicates = list(coll.aggregate(pipeline, allowDiskUse=True))
    removed = 0
    for g in duplicates:
        ids = g.get("ids", [])
        to_delete = ids[1:]  # احتفظ بالأول واحذف الباقي
        if to_delete:
            res = coll.delete_many({"_id": {"$in": to_delete}})
            removed += res.deleted_count
    if removed:
        print(f"🧹 Removed {removed} duplicated documents from {coll.name} on key '{key}'")
    return removed

def load_mongo(players, stats):
    players_dicts = [player_to_dict(p) for p in players]
    stats_dicts   = [stat_to_dict(s) for s in stats]
 
    pd.DataFrame(players_dicts).to_csv("data/raw/players.csv", index=False)
    pd.DataFrame(stats_dicts).to_csv("data/raw/stats.csv", index=False)

    with open("data/raw/players.json", "w") as f:
        json.dump(players_dicts, f, indent=2)
    with open("data/raw/stats.json", "w") as f:
        json.dump(stats_dicts, f, indent=2)

  
    try:
        deduplicate_collection(mdb.raw_players, "id")
        deduplicate_collection(mdb.raw_stats, "id")
    except Exception as e:
        print(f"⚠️ Dedup warning: {e}")

   
    try:
        mdb.raw_players.create_index("id", unique=True)
        mdb.raw_stats.create_index("id", unique=True)
    except Exception as e:
        print(f"⚠️ Index creation warning: {e}")
 
    if players_dicts:
        ops = [
            UpdateOne({"id": d.get("id")}, {"$set": d}, upsert=True)
            for d in players_dicts if d.get("id") is not None
        ]
        if ops:
            try:
                mdb.raw_players.bulk_write(ops, ordered=False)
            except errors.BulkWriteError as e:
                print(f"⚠️ Players bulk write warning: {e.details}")

    if stats_dicts:
        ops = [
            UpdateOne({"id": d.get("id")}, {"$set": d}, upsert=True)
            for d in stats_dicts if d.get("id") is not None
        ]
        if ops:
            try:
                mdb.raw_stats.bulk_write(ops, ordered=False)
            except errors.BulkWriteError as e:
                print(f"⚠️ Stats bulk write warning: {e.details}")
