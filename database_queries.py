#! /usr/bin/env python3
import sqlite3
import uuid

# connection = sqlite3.connect("DB/answers.db")
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM games")
# looking_for = cursor.fetchall()
# print(looking_for)


username = "billythomas"
sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
connection = sqlite3.connect("DB/Shards/user_profiles.db")
cursor = connection.cursor()
cursor.execute("SELECT unique_id FROM users where username = ?", [username])
user_id = cursor.fetchall()[0][0]
print(user_id)


con2 = sqlite3.connect("DB/answers.db")
cur2 = con2.cursor()
cur2.execute("SELECT MIN(answer_id), MAX(answer_id) FROM games")
looking_for = cur2.fetchall()
min_id = looking_for[0][0]
max_id = looking_for[0][1]
game_id = randint(min_id, max_id)
