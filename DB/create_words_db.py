#! /usr/bin/env python3

"""Initializes and populates word list database"""

import sqlite3
import re
import os.path


def get_word_list():
    """Retrieves words and ignores offensive offensive"""
    all_words = []
    with open("/usr/share/dict/words", "r") as word_file:
        for line in word_file:
            if len(line) == 6:
                word = line.replace("\n", "")
                if re.search('[a-z]{5}', word):
                    all_words.append(word)
    offensive_words = []
    with open("offensive.txt", "r") as word_file:
        for line in word_file:
            if len(line) == 6:
                word = line.replace("\n", "")
                if re.search('[a-z]{5}', word):
                    offensive_words.append(word)
    five_letter_words = []
    word_id = 1
    for i, words in enumerate(all_words):
        if words not in offensive_words:
            a_word = (words,)
            five_letter_words.append(a_word)
            word_id += 1
    return five_letter_words


def make_database(words_five):
    """Using the words retrived make a database of words"""
    file_exists = os.path.exists("words.db")
    connection = sqlite3.connect("words.db")
    cursor = connection.cursor()
    if not file_exists:
        cursor.execute("CREATE TABLE words (word CHAR(5) PRIMARY KEY)")
        cursor.executemany("INSERT INTO words VALUES(?)", words_five)
        connection.commit()
    else:
        print("DB already made")
    connection.close()


if __name__ == '__main__':
    words_five = get_word_list()
    make_database(words_five)
