import pandas as pd
import numpy as np


class WordleSolver:
    """A class for playing a Wordle Style game. Designed around building a simple
    solver for the Irish language version of the game Foclach.

    Object must be instantiated with a dataframe having the column structure as follows:

    word 	chars 	1 	2 	3 	4 	5   ... [letter_tokens]

    Usage: instantiate a game using the corpus
        >>> g = WordleGame(corpus_df)
        >>> guess = g.get_next_guess(); guess

        # input the guess into the game and get the clues in return
        # you can either use an array of ['gray', 'yellow', 'green']
        # or you can use a string. # If using a string, the key is:
        #   g = green (letter exists in correct location)
        #   y = yellow (letter exists but not in this location)
        #   r = gray (letter does not exists in the word)

        >>> g.update_clues_and_guess('gyrrr')
        >>> guess = g.get_next_guess(); guess

        ...


    :class: WordleGame

    :param words_df: the corpus, as a dataframe structured with columns as
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        word 	 	1 	2 	3 	4 	5   ... [letters] ... score
        - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        and each row as a token

       	word 	 	1 	2 	3 	4 	5 	a 	    c 	    á 	    ...     score
        srian 	    s 	r 	i 	a 	n 	True 	False 	False 	...     0.1
        hairc 	    h 	a 	i 	r 	c 	True 	True 	False 	...     0.001
        chiar 	    c 	h 	i 	a 	r 	True 	True    False   ...     0.2

        The final score column is used to create the probability distribution
        of tokens from which the guess will be selected
    """

    def __init__(self, words_df):
        self.current_masks = []
        self.guesses = []
        self.guesses_and_results = []
        # Ensure score column is numeric when initializing
        words_df['score'] = pd.to_numeric(words_df['score'], errors='coerce').fillna(0)
        self.corpus = words_df
        self.filtered_corpus = words_df

    def make_guess(self):
        # Convert to float and handle any potential issues
        scores = self.filtered_corpus['score'].astype(float)
        total_score = scores.sum()
        if total_score == 0:
            # If all scores are 0, use uniform distribution
            probabilities = np.ones(len(scores)) / len(scores)
        else:
            probabilities = scores / total_score

        guess_idx = np.random.choice(self.filtered_corpus.index, p=probabilities.values)
        return self.filtered_corpus.loc[guess_idx]['word']

    def filter_db_from_masks(self):
        if len(self.current_masks) > 0:
            mask = np.array(self.current_masks).prod(axis=0).astype(np.bool_)
            self.filtered_corpus = self.corpus[mask]
        return self.filtered_corpus

    def next_best_guesses(self):
        return self.filtered_corpus

    def masks_from_guess(self, guess, list_of_colors):
        # takes a word and list of colors, the pandas dataframe (db), and the
        # list of known masks, if it exists
        # outputs a mask to filter the words based on
        # the constraints resulting from that guess
        # input of list of colors can either be a list of ['Gray', 'Green', 'Yellow']
        # or a string of ['GYR'], where R is gray
        db = self.corpus
        for idx, l in enumerate(guess):
            if list_of_colors[idx].lower() in ["g", "green"]:
                print(f'{l} g')
                # if it's green then the letter in position idx is correct
                # which means the word has the letter, and it's in that position
                position = str(idx+1) # this is the string position to reference the db
                self.current_masks.append(db[position] == l)
                self.current_masks.append(db[l] == True)
            elif list_of_colors[idx].lower() in ["y", "yellow"]:
                print(f'{l} y')
                # here the letter is in the secret word, but
                # the letter is not in the right position
                position = str(idx+1) # this is the string position to reference the db
                # so we know that the letter at this position is not this letter
                self.current_masks.append(db[position] != l)
                # and we know that the letter is in the word
                self.current_masks.append(db[l] == True)
            elif list_of_colors[idx].lower() in ["r", "gray", "grey"]:
                print(f'{l} r')
                # here the letter is not in the secret word
                self.current_masks.append(db[l] == False)
        return self.current_masks

    def list_possible_guesses(self):
        filtered_db = self.filter_db_from_masks()
        return filtered_db['word']

    def get_next_guess(self):
        filtered_db = self.filter_db_from_masks()
        guess = self.make_guess()
        self.guesses.append(guess)
        return guess

    def update_clues_and_guess(self, clues, guess=None):
        if guess is None:
            guess = self.guesses[-1]
        self.masks_from_guess(guess, clues)

    @staticmethod
    def evaluate_guess(guess, secret_word):
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
