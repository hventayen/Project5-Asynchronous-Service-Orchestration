# Project4-NoSQL
## Joseph Nasr
## Harrold Ventayen
## Samuel Valls
## Kevin Garcia
### Databases (Executables located in DB/):
Initialize database: execute create_stats_db.sh in the terminal
Create shards: execute create_shards.py in the terminal
### Starting services:
#### Standalone:
uvicorn m1:app --reload
uvicorn m2:app --reload
uvicorn m3:app --reload
uvicorn m4:app --reload
#### Using Traefik:
./traefik --configFile=traefik.toml
foreman start -m 'word=1, game=1, stat=3'
### Steps For Materialized Views Using Cron
Step 1: make crontab from the terminal using this command
crontab -e
Step 2: press '2' to edit crontab within the terminal
Step 3: insert this command at the end of the file
*/10 * * * * /usr/bin/python3 (insert path of project4 file here)/create_materialized_views.py
Step 4: press 'enter' to install crontab in the /tmp/crontab directory
Step 5: execute services
foreman start -m 'stat=3, state=1'
Step 6: go to link
http://127.0.0.1:9999/stats/m3/docs
Step 7: change lines 16, 18, 19, 20 to switch the path with your absolute path for the databases
Example:
/home/(insert username here)/Project4-NOSQL/DB/Shards/stats1.db
Step 8: test out microservice for leaderboards