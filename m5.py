#! /usr/bin/env python3
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field
import uuid
import requests
import asyncio
from datetime import date
"""TODO: Update README,
Fix other TODOS:
    See m3.py TODO,
    See m5.py TODO,
Do Error Checking:
    Check if when a player loses a game, the 'fail' variable increases
    Check if when the player wins a game, date is the same as date played
        Check to see if the players current streak goes up when they win multi-times
    """

app = FastAPI()

@app.post('/game/new')
async def start_new_game(username: str):

    ret1 = httpx.get(f'http://127.0.0.1:5200/stats/games/{username}')
    if ret1.status_code == httpx.codes.OK:
        game_id = ret1.json()['game_id']
        user_id = ret1.json()['user_id']
        ret2 = httpx.post(f'http://127.0.0.1:5300/game/{game_id}?user_id={user_id}')
        if ret2.status_code == httpx.codes.OK:
            return ret2.json()
        else:
            ret3 = httpx.get(f'http://127.0.0.1:5300/game/{game_id}?user_id={user_id}')
            if ret3.status_code == httpx.codes.OK:
                last_word = ret3.json()['guess_list']
                tmp_word = ""
                for word in range(len(last_word)):
                    if len(last_word[word]) > 0:
                        tmp_word = last_word[word]

                ret4 = httpx.get(f'http://127.0.0.1:5100/games/{game_id}?guess={tmp_word}')
                if ret4.status_code == httpx.codes.OK:
                    my_dict = ret3.json()
                    my_dict.update({"letter_colors": ret4.json()['letter colors']})
                    return my_dict
                else:
                    return {"Error Code" : ret4.status_code, "detail" : ret4.json()['detail']}
            else:
                return {"Error Code" : ret3.status_code, "detail" : ret3.json()['detail']}
    else:
        return {"Error Code" : ret1.status_code, "detail" : ret1.json()['detail']}


@app.post('/game/{game_id}')
async def guess_a_word(game_id: int, user_id: uuid.UUID, guess: str):
    ret1 = httpx.get(f'http://127.0.0.1:5000/words/{guess}')
    if ret1.status_code == httpx.codes.OK:
        L = []
        async with httpx.AsyncClient() as client:
            L = await asyncio.gather(
                client.patch(f'http://127.0.0.1:5300/game/{game_id}?user_id={user_id}&user_word={guess}'),
                client.get(f'http://127.0.0.1:5100/games/{game_id}?guess={guess}')
            )
        for code in L:
            if code.status_code == httpx.codes.OK:
                continue
            else:
                return {"Error Code" : code.status_code, "detail" : code.json()['detail']}
        ret2 = L[0]
        ret3 = L[1]
        if ret2.json()['guesses_left'] == 0 and not ret3.json()['status']:
            m3 = httpx.post(f'http://127.0.0.1:5200/stats/games/{game_id}?unique_id={user_id}', json={
                       'status': False,
                       'timestamp': str(date.today()),
                       'number_of_guesses': ret2.json()['guesses_left']
                   })
            if m3.status_code == httpx.codes.OK:
                ret4 = httpx.get(f"http://127.0.0.1:5200/stats/games/{user_id}/")
                if ret4.status_code == httpx.codes.OK:
                    ret4_dict = ret4.json()
                    ret4_dict.update({"status" : m3.json()['status'], "remaining" : ret2.json()['guesses_left']})
                    return ret4_dict
                else:
                    return {"Error Code" : ret4.status_code, "detail" : ret4.json()['detail']}
            else:
                return {"Error Code" : m3.status_code, "detail" : m3.json()['detail']}
        elif ret3.json()['status']:
            m3 = httpx.post(f'http://127.0.0.1:5200/stats/games/{game_id}?unique_id={user_id}', json={
                        'status': True,
                        'timestamp': str(date.today()),
                        'number_of_guesses': ret2.json()['guesses_left']
                    })
            if m3.status_code == httpx.codes.OK:
                ret4 = httpx.get(f"http://127.0.0.1:5200/stats/games/{user_id}/")
                if ret4.status_code == httpx.codes.OK:
                    ret4_dict = ret4.json()
                    ret4_dict.update({"status" : m3.json()['status'], "remaining" : ret2.json()['guesses_left']})
                    return ret4_dict
                else:
                    return {"Error Code" : ret4.status_code, "detail" : ret4.json()['detail']}
            else:
                return {"Error Code" : m3.status_code, "detail" : m3.json()['detail']}
        else:
            my_dict = ret2.json()
            my_dict.update({"letter_colors" : ret3.json()['letter colors']})
            return my_dict
    else:
        return {"Error Code" : ret1.status_code, "detail" : ret1.json()['detail']}
