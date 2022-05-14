#! /usr/bin/env python3
import httpx
from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel, Field




app = FastAPI()

@app.post('/game/new')
async def start_new_game(username: str):
    # TODO:
        # Parameters may need to be editted
        # Plan of action:
            # Find the user_id for the specified username
                #  Microservice 4(5300): @app.post('/game/{game_id}')
                    ## Need to change input to receive a username
                    ## status inside of result may need to change to a string
            # Create the actual game:
                # Microservice 4(5300): @app.post('/game/{game_id}')
                    ## user_id needs to be changed to recieve a uuid


        # ret = httpx_fucntion_call(link)
    ret = httpx.post('http://127.0.0.1:5300/game/billythomas')
    return ret.json()



@app.post('/game/{game_id}')
async def guess_a_word(game_id: int, user_id: int, guess: str):
    # TODO:
        # Parameters may need to be editted
        # Verify the guess is a word in dictionary
            # Microservice 1(5000): @app.get("/words/{letters}")
        # Check if user has guess remaining:
            # In Microservice 4 an exception is thrown if a guess is made when
            # max has been reached. The endpoint is: @app.patch('/game/{game_id}')
        # Record the guess and update the number of guesses remaining
            # Microservice 4: @app.patch('/game/{game_id}')
        # Check to see if the guess is correct
            # Microservice 2(5100): @app.get("/games/{answer_id}")
                # If return[status]: Its a win
                # If not return[status]: its not win
        # Record State
            #  Microservice 3: @app.post("/stats/games/{game_id}")
        # Return score
            # Microservice 3: @app.get("/stats/games/{unique_id}/")

    pass
