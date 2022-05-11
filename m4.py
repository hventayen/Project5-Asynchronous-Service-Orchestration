#! /usr/bin/env python3
import sqlite3
import redis
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field


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

@app.post('/game/{game_id}')
async def new_game(game_id: int, user_id: int):
    r = redis.Redis(host='localhost', port=6379, db=0)
    if r.exists(f"{user_id} : {game_id} : guess_list"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Game already played"
        )
    r.lpush(f"{user_id} : {game_id} : guess_list", "", "", "", "", "", "")
    r.set(f"{user_id} : {game_id} : guesses_left", 6)

    player_game = {
        "game_id": game_id,
        "user_id": user_id,
        "detail": "Game Created"
        }
    return player_game

@app.patch('/game/{game_id}')
async def update_game(game_id: int, user_id: int, user_word: str):
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
    return player_game

@app.get('/game/{game_id}')
async def grab_game(game_id: int, user_id: int):
    r = redis.Redis(host='localhost', port=6379, db=0)
    guesses_left = int((r.get(f"{user_id} : {game_id} : guesses_left").decode("UTF-8")))
    guess_list = r.lrange(f"{user_id} : {game_id} : guess_list", 0, 6 - guesses_left - 1)

    player_game = {
        "game_id": game_id,
        "user_id": user_id,
        "guess_list": guess_list,
        "guesses_left": guesses_left
    }
    return player_game
