#! /usr/bin/env python3

"""Microservice 1: Checking guesses from word list"""

import contextlib
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, status


def get_db():
    """Connect words.db"""
    with contextlib.closing(sqlite3.connect("DB/words.db", check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db


app = FastAPI()


@app.get("/words/{letters}")
async def valid_word(letters: str, db: sqlite3.Connection = Depends(get_db)):
    """Check for valid word in word list"""
    cur = db.execute("SELECT word FROM words WHERE word = ?", [letters])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Word not found"
        )
    return {"word": looking_for[0][0]}


@app.post("/words/{letters}")
async def add_guess(letters: str, db: sqlite3.Connection = Depends(get_db)):
    """Add possible guess to word list"""
    cur = db.execute("SELECT word FROM words WHERE word = ?", [letters])
    looking_for = cur.fetchall()
    if looking_for:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Word already exists"
        )
    if len(letters) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Word not length 5"
        )
    db.execute("INSERT INTO words VALUES(?)", [letters])
    db.commit()
    return {"details": "successfully added", "word": f"{letters}"}


@app.delete("/words/{letters}")
async def delete_guess(letters: str, db: sqlite3.Connection = Depends(get_db)):
    """Delete possible guess from word list"""
    cur = db.execute("SELECT word FROM words WHERE word = ?", [letters])
    looking_for = cur.fetchall()
    if not looking_for:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Word not found"
        )
    db.execute("DELETE FROM words WHERE word = ?", [letters])
    db.commit()
    return {"details": f"successfully removed", "word": f"{letters}"}
