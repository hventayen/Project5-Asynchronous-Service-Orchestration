#! /usr/bin/env python3
import sqlite3
import redis
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field


def get_db():
    """Connect words.db"""
    with contextlib.closing(sqlite3.connect("DB/stats.db", check_same_thread=False)) as db:
        db.row_factory = sqlite3.Row
        yield db


app = FastAPI()

@app.post('/game/new')
async def start_new_game(game_id: int, user_id: int):
    # TODO:
        # Parameters may need to be editted
    pass


@app.post('/game/{game_id}')
async def guess_a_word(game_id: int, user_id: int):
    # TODO:
        # Parameters may need to be editted
    pass
