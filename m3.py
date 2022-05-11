#! /usr/bin/env python3

"""Microservice 3: Tracking users' wins and losses"""

import contextlib
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
from datetime import date
from math import trunc
import uuid
import redis

class Guesses(BaseModel):
        guess1: int = Field(0, alias='1')
        guess2: int = Field(0, alias='2')
        guess3: int = Field(0, alias='3')
        guess4: int = Field(0, alias='4')
        guess5: int = Field(0, alias='5')
        guess6: int = Field(0, alias='6')
        fail: int
# Edit guess1 to 1, guess2 to 2, etc.
class Stats(BaseModel):
    """Json format for a player stats"""
    # Should we add username????????????????
    currentStreak: int
    maxStreak: int
    guesses: Guesses
    winPercentage: float
    gamesPlayed: int
    gamesWon: int
    averageGuesses: int

class Result(BaseModel):
    status: bool
    timestamp: str
    number_of_guesses: int


def get_db():
    """Connect words.db"""
    with contextlib.closing(sqlite3.connect("DB/stats.db", check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db


app = FastAPI()


@app.post("/stats/games/{game_id}")
async def add_game_played(game_id: int, unique_id: uuid.UUID, result: Result):
    """Posting a win or loss"""
    # post into games
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    if (int(unique_id) % 3 == 0):
        con = sqlite3.connect("DB/Shards/stats1.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()
    elif (int(unique_id) % 3 == 1):
        con = sqlite3.connect("DB/Shards/stats2.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()
    else:
        con = sqlite3.connect("DB/Shards/stats3.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()

    db.execute("ATTACH DATABASE 'DB/Shards/user_profiles.db' As 'up'")

    cur = db.execute("SELECT user_id FROM up.users WHERE unique_id = ?", [unique_id])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    tmp_user_id = looking_for[0][0]
    cur = db.execute("SELECT game_id, unique_id FROM games WHERE game_id = ? AND unique_id = ?", [game_id, unique_id])
    looking_for = cur.fetchall()
    if looking_for:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Game for player already exists"
        )
    cur = db.execute("INSERT INTO games VALUES(?,?,?,?,?,?)", [tmp_user_id, game_id, result.timestamp, result.number_of_guesses, result.status, unique_id])
    con.commit()
    db.close()
    return result

@app.get("/stats/games/{unique_id}/")
async def retrieve_player_stats(unique_id: uuid.UUID):
    """Getting stats of a user"""
    # use table: games
    sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
    sqlite3.register_adapter(uuid.UUID, lambda u: memoryview(u.bytes_le))
    if (int(unique_id) % 3 == 0):
        con = sqlite3.connect("DB/Shards/stats1.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()
    elif (int(unique_id) % 3 == 1):
        con = sqlite3.connect("DB/Shards/stats2.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()
    else:
        con = sqlite3.connect("DB/Shards/stats3.db", detect_types=sqlite3.PARSE_DECLTYPES)
        db = con.cursor()

    db.execute("ATTACH DATABASE 'DB/Shards/user_profiles.db' As 'up'")

    cur = db.execute("SELECT unique_id FROM up.users WHERE unique_id = ?", [unique_id])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    today = date.today()
    the_date = today.strftime("%Y-%m-%d")
    max_streak = current_streak = 0
    cur = db.execute("SELECT streak FROM streaks WHERE unique_id = ? AND ending = ?", [unique_id, the_date])
    looking_for = cur.fetchall()
    if looking_for:
        current_streak = looking_for[0][0]
    cur = db.execute("SELECT MAX(streak) FROM streaks WHERE unique_id = ?", [unique_id])
    looking_for = cur.fetchall()
    if looking_for:
        max_streak = looking_for[0][0]
        if max_streak == None:
            max_streak = 0
    guess_list = []
    i = 0
    while len(guess_list) < 6:
        cur = db.execute("SELECT COUNT(game_id) FROM games WHERE unique_id = ? AND guesses = ?", [unique_id, i+1])
        guess = cur.fetchall()[0][0]
        guess_list.append(int(guess))
        i += 1
    cur = db.execute("SELECT COUNT(game_id) FROM games WHERE unique_id = ? AND won = ?", [unique_id, False])
    games_lost = cur.fetchall()[0][0]
    cur = db.execute("SELECT COUNT(game_id) FROM games WHERE unique_id = ?", [unique_id])
    games_played = cur.fetchall()[0][0]
    cur = db.execute("SELECT COUNT(game_id) FROM games WHERE unique_id = ? AND won = ?", [unique_id, True])
    games_won = cur.fetchall()[0][0]
    if games_played != 0:
        win_percentage = trunc((games_won / games_played) * 100)
    else:
        win_percentage = trunc(0.0)
    average_guesses = sum(guess_list) // 6
    stat = Stats(currentStreak=current_streak, maxStreak=max_streak, guesses=Guesses(fail=0), winPercentage=win_percentage, gamesPlayed=games_played, gamesWon=games_won, averageGuesses=average_guesses)
    stat.guesses.guess1 = guess_list[0]
    stat.guesses.guess2 = guess_list[1]
    stat.guesses.guess3 = guess_list[2]
    stat.guesses.guess4 = guess_list[3]
    stat.guesses.guess5 = guess_list[4]
    stat.guesses.guess6 = guess_list[5]
    db.close()
    return stat


@app.get("/stats/wins/")
async def retrieve_top_wins():
    """Getting the top 10 users by number of wins"""
    # use view: wins
    # Get number of wins
    r = redis.Redis(host='localhost', port=6379, db=0)
    set_key = f"Top 10 wins"
    score_list = r.zrevrange(set_key, 0, -1, withscores = True)

    return {"TopWinners": [{"username": tup[0], "wins": tup[1]} for tup in score_list[:10]]}

@app.get("/stats/streaks/")
async def retrieve_top_streaks(db: sqlite3.Connection = Depends(get_db)):
    """Getting the top 10 users by streak"""
    # use view: streaks
    r = redis.Redis(host='localhost', port=6379, db=0)
    set_key = f"Top 10 streaks"
    score_list = r.zrevrange(set_key, 0, -1, withscores = True)
    for tup in score_list:
        tup[0].decode("UTF-8")
    # NOT SURE HOW YOU WOULD LIKE US TO OUTPUT THESE?????????????????????
    return {"TopStreaks": [{"username": tup[0], "streaks": tup[1]} for tup in score_list[:10]]}
