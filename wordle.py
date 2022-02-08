import pandas as pd
import numpy as np
import re

class WordleGame:
    """This is a class for playing a Wordle Style game, given a corpus of
    words organized into a dataframe with the column structure as follows:
    word 	chars 	1 	2 	3 	4 	5   ... [letter_tokens]
    
    Usage: instantiate a game using the corpus ```g = WordleGame(corpus_df)```
        >>> guess = g.get_next_guess(); guess
        # input the guess into the game and get the clues in return
        # you can either use an array of ['gray', 'yellow', 'green'] 
        # or you can use a string. # If using a string, the key is:
        #   g = green (letter exists in correct location)
        #   y = yellow (letter exists but not in this location)
        #   r = gray (letter does not exists in the word)        
        
        >>> g.update_clues_and_guess('gyrrr')
    
    
    :class: WordleGame

    :param words_df: the corpus, as a dataframe structured with columns as 
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        word 	chars 	1 	2 	3 	4 	5   ... [letters]
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
        
        and each row as a token
        
    :usage: 
    """
    
    def __init__(self, words_df):
        self.current_masks = []
        self.guesses = []
        self.guesses_and_results = []
        self.corpus = words_df
        
    def make_guess(self, filtered_db):
        guess_idx = np.random.choice(filtered_db.index, p=(filtered_db['score'] / filtered_db['score'].sum()).values)
        return db.loc[guess_idx]['word']
    
    def filter_db_from_masks(self, masks, db):
        current_masks = np.array(masks).prod(axis=0).astype(np.bool_)
        return db[current_masks]    
    
    def next_best_guesses(self):
        if self.current_masks is None or len(self.current_masks) == 0:
            filtered_db = self.corpus
        else:
            filtered_db = self.filter_db_from_masks(self.current_masks, self.corpus)
        return filtered_db
    
    def masks_from_guess(self, guess, list_of_colors, db, masks=[]):
        # takes a word and list of colors, the pandas dataframe (db), and the
        # list of known masks, if it exists
        # outputs a mask to filter the words based on
        # the constraints resulting from that guess
        # input of list of colors can either be a list of ['Gray', 'Green', 'Yellow']
        # or a string of ['GYR'], where R is gray
        for idx, l in enumerate(guess):
            if list_of_colors[idx].lower() in ["g", "green"]:
                # if it's green then the letter in position idx is correct
                # which means the word has the letter, and it's in that position
                position = str(idx+1) # this is the string position to reference the db
                masks.append(db[position] == l)
                masks.append(db[l] == True)
            elif list_of_colors[idx].lower() in ["g", "yellow"]:
                # here the letter is in the secret word, but 
                # the letter is not in the right position
                position = str(idx+1) # this is the string position to reference the db
                # so we know that the letter at this position is not this letter
                masks.append(db[position] != l)            
                # and we know that the letter is in the word
                masks.append(db[l] == True)
            elif list_of_colors[idx].lower() in ["r", "gray", "grey"]:
                # here the letter is not in the secret word
                masks.append(db[l] == False)
        return masks
    
    def evaluate_guess(self, guess, secret_word):
        # evaluates a guess against the secret_word and outputs
        # the list of colors for that word
        colors = []
        for idx, l in enumerate(guess):
            if secret_word[idx] == l:
                v = 'Green'
            elif l in secret_word:
                v = 'Yellow'
            else:
                v = 'Gray'
            colors.append(v)
        return colors
    
    def get_next_guess(self):
        possibles = self.next_best_guesses()        
        guess = possibles.iloc[0]['word']
        self.guesses.append(guess)
        return guess
    
    def update_clues_and_guess(self, clues, guess=None):
        if guess is None:
            guess = self.guesses[-1]
        self.current_masks = self.masks_from_guess(guess, clues, self.corpus, 
                                                   masks=self.current_masks)
