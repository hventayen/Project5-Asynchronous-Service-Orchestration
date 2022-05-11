#! /usr/bin/env python3
import sqlite3
import redis
import uuid
# Testing Cron
# import random
# from datetime import datetime

# now = datetime.now()
# with open('/home/student/Desktop/Project4-NOSQL/logs.txt', 'a') as f:
#    f.write('{}\n'.format(now))

def make_top_10s(view_dec):
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    con = sqlite3.connect("/home/student/Desktop/Project4-NOSQL/DB/Shards/stats1.db", detect_types=sqlite3.PARSE_DECLTYPES)
    db = con.cursor()
    db.execute("ATTACH DATABASE '/home/student/Desktop/Project4-NOSQL/DB/Shards/user_profiles.db' As 'up'")
    db.execute("ATTACH DATABASE '/home/student/Desktop/Project4-NOSQL/DB/Shards/stats2.db' As 's2'")
    db.execute("ATTACH DATABASE '/home/student/Desktop/Project4-NOSQL/DB/Shards/stats3.db' AS 's3'")
    if view_dec == "wins":
        column = "number_won"
    else:
        column = "streak"
    cur = db.execute(f"SELECT username, {column} FROM {view_dec} JOIN up.users ON {view_dec}.unique_id=up.users.unique_id ORDER BY {column} DESC LIMIT 10")
    looking_for = cur.fetchall()
    cur = db.execute(f"SELECT username, {column} FROM s2.{view_dec} JOIN up.users ON s2.{view_dec}.unique_id=up.users.unique_id ORDER BY {column} DESC LIMIT 10")
    looking_for += cur.fetchall()
    cur = db.execute(f"SELECT username, {column} FROM s3.{view_dec} JOIN up.users ON s3.{view_dec}.unique_id=up.users.unique_id ORDER BY {column} DESC LIMIT 10")
    looking_for += cur.fetchall()
    looking_for.sort(key = lambda x: x[1])
    max_score = looking_for[-1][1]

    min_score = looking_for[0][1]
    r = redis.Redis(host='localhost', port=6379, db=0)
    set_key = f"Top 10 {view_dec}"
    p = r.pipeline()
    p.multi()
    scores = {}
    for tup in looking_for:
        scores[tup[0]] = tup[1]
        r.zrem(set_key, tup[0])
    r.zadd(set_key, scores)
    p.execute()
    con.close()
    r.close()
    
make_top_10s("wins")
make_top_10s("streaks")



