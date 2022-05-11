#! /usr/bin/env python3

"""Loads database of wordle_script answers"""

import sqlite3
import json
import os.path


def get_answers():
    """Loads all answers from wordle_script into list1"""
    # Open the wordle answer JSON file
    file = open("answers.json")

    # Load all answers into a list1
    data = json.load(file)

    # Create list1 of answers with following pair (answer, answer_id)
    all_answers = []
    for answer in data:
        all_answers.append((answer,))
    return all_answers


def get_database(list1):
    """Creates database of wordle answers"""
    file_exists = os.path.exists("answers.db")
    connection = sqlite3.connect("answers.db")
    cursor = connection.cursor()
    if not file_exists:
        cursor.execute(
            "CREATE TABLE games (game_answers CHAR(5), answer_id INTEGER PRIMARY KEY)"
        )
        cursor.executemany("INSERT INTO games VALUES(?, NULL)", list1)
        connection.commit()
    else:
        print("DB already made")
    connection.close()


if __name__ == "__main__":
    WORDLE_ANSWERS = get_answers()
    get_database(WORDLE_ANSWERS)
