#! /usr/bin/env python3

"""Microservice 2"""

import contextlib
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel


class Game(BaseModel):
    """Json format for a game"""
    word: str
    game_id: int


def get_db():
    """Gets database handle"""
    with contextlib.closing(sqlite3.connect("DB/answers.db", check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db

app = FastAPI()

@app.get("/games/{answer_id}")
async def check_guess(answer_id: int, guess: str, db: sqlite3.Connection = Depends(get_db)):
    """Checks to see if a guess is correct, if not return color values of each letter"""
    cur = db.execute("SELECT game_answers FROM games WHERE answer_id = ?", [answer_id])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Id not found"
        )
    wordle_of_day = looking_for[0][0]
    if guess == wordle_of_day:
        return {"detail": "Guess is correct!"}
    color_list = []
    for index, letter in enumerate(guess):
        color = "Gray"
        if wordle_of_day[index] == guess[index]:
            color = "Green"
        else:
            if letter in wordle_of_day:
                color = "Yellow"
        color_list.append(color)
    return {"letter colors" : [f"{letter}: {color_list[index]}" for index, letter in enumerate(guess)]}


@app.put("/games/")
async def change_daily_word(game: Game, db: sqlite3.Connection = Depends(get_db)):
    """Change the word of a given game"""
    cur = db.execute("SELECT answer_id FROM games WHERE answer_id = ?", [game.game_id])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Id not found"
        )
    if len(game.word) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Word not length 5"
        )
    db.execute("Update games SET game_answers = ? WHERE answer_id = ?", [game.word, game.game_id])
    db.commit()
    return game
