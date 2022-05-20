# Project5-Asynchronous-Service-Orchestration
## Joseph Nasr
## Harrold Ventayen
## Mohammad Qazi
## Kevin Sierras
### Databases (Executables located in DB/):
Initialize database: execute create_words_db.py, create_answer_db.py, and create_stats_db.sh in the terminal

Create shards folder: create empty folder named "Shards" in folder "DB"

Create shards: execute create_shards.py in the terminal

### Starting services:
#### Standalone:
uvicorn m1:app --reload

uvicorn m2:app --reload

uvicorn m3:app --reload

uvicorn m4:app --reload

uvicorn m5:app --reload

#### Using Microservice 5 in terminal:
foreman start

### Steps For Testing Microservice 5:
Step 1: Go to docs page for link given after executing microservice 5

ex: http://127.0.0.1:5400/docs

Step 2: Insert a username registered on Microservice 3's streaks for first endpoint

ex: ucohen

Step 3: Copy game_id and user_id from the JSON response of first endpoint

ex:

(game_id) 2068

(user_id) 123e4567-e89b-12d3-a456-426614174000

Step 4: Insert game_id and user_id with a 5 letter word guess for the game into second endpoint

(game_id) 2068

(user_id) 123e4567-e89b-12d3-a456-426614174000

(guess) break

Step 5: Give 5 more guesses with the same game_id and user_id with a 5 letter word guess to get win or loss

ex:

brine

fling

great

trade

learn
