#! /usr/bin/env python3
import uuid
import sqlite3

def print_all():
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    con = sqlite3.connect("DB/Shards/user_profiles.db", detect_types=sqlite3.PARSE_DECLTYPES)
    db = con.cursor()
    cur = db.execute("SELECT unique_id FROM users")
    for i in cur.fetchall():
        print(i)


if __name__ == '__main__':
    print_all()