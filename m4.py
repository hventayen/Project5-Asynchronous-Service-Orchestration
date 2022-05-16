#! /usr/bin/env python3
import sqlite3
import redis
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from random import randint
import uuid
def get_db():
    """Connect words.db"""
    with contextlib.closing(sqlite3.connect("DB/stats.db", check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db


class Result(BaseModel):
    game_id: int
    user_id: int
    guess_list: list
    guesses_left: int

app = FastAPI()

@app.post('/game/{username}')
async def new_game(username: str):
    # Example Link: http://127.0.0.1:5300/game/{1}?{user_id=1}
    """Changing parameters to only accept a username; added a connection to
    user_profiles shard, to get the uuid assocaited to username, also generate
    a new game id based on game ids inside of answers.db"""
    r = redis.Redis(host='localhost', port=6379, db=0)
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    connection = sqlite3.connect("DB/Shards/user_profiles.db", detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = connection.cursor()
    cursor.execute("SELECT unique_id FROM users where username = ?", [username])
    user_id = cursor.fetchall()[0][0]
    con2 = sqlite3.connect("DB/answers.db")
    cur2 = con2.cursor()
    cur2.execute("SELECT MIN(answer_id), MAX(answer_id) FROM games")
    looking_for = cur2.fetchall()
    min_id = looking_for[0][0]
    max_id = looking_for[0][1]
    game_id = randint(min_id, max_id)
    while r.exists(f"{user_id} : {game_id} : guess_list"):
        game_id = randint(min_id, max_id)

    r.lpush(f"{user_id} : {game_id} : guess_list", "", "", "", "", "", "")
    r.set(f"{user_id} : {game_id} : guesses_left", 6)

    player_game = {
        "status": "new",
        "game_id": game_id,
        "user_id": user_id
        }
    r.close()
    return player_game

@app.patch('/game/{game_id}')
async def update_game(game_id: int, user_id: uuid.UUID, user_word: str):
    # http://127.0.0.1:5300/game/{1}?{user_id=10}
    r = redis.Redis(host='localhost', port=6379, db=0)

    if not r.exists(f"{user_id} : {game_id} : guess_list"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    list_count = int((r.get(f"{user_id} : {game_id} : guesses_left").decode("UTF-8")))

    if not list_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Max guesses reached"
        )

    r.lset(f"{user_id} : {game_id} : guess_list", 6 - list_count, user_word)
    list_count -= 1
    guess_list = r.lrange(f"{user_id} : {game_id} : guess_list", 0, 6 - list_count - 1)
    r.set(f"{user_id} : {game_id} : guesses_left", list_count)

    player_game = {
        "game_id": game_id,
        "user_id": user_id,
        "guess_list": guess_list,
        "guesses_left": list_count
    }
    r.close()
    return player_game

@app.get('/game/{game_id}')
async def grab_game(game_id: int, user_id: int):
    # http://127.0.0.1:5300/game/{1}?{user_id=10}&{user_word=apple}
    r = redis.Redis(host='localhost', port=6379, db=0)
    guesses_left = int((r.get(f"{user_id} : {game_id} : guesses_left").decode("UTF-8")))
    guess_list = r.lrange(f"{user_id} : {game_id} : guess_list", 0, 6 - guesses_left - 1)

    player_game = {
        "game_id": game_id,
        "user_id": user_id,
        "guess_list": guess_list,
        "guesses_left": guesses_left
    }
    r.close()
    return player_game
