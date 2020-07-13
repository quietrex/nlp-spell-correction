# -*- coding: utf-8 -*-
"""
Completed by team:
    
    Goal: To build a spell check system by using bigram
    This python file is meant to be all the GUI needed functions will be in here. including core functions
    
@author: team
"""

# Importing needed only library
import string
import json, collections
import spacy
import numpy as np
from collections import Counter
import re

# Get the configuration files
from config import dic_path, bigram_freq_path, bigrams_text_path
nlp = spacy.load("en")


# Default text path into dicWords variable
dictionary_freq = json.load(open(dic_path))
bigram_freq = json.load(open(bigram_freq_path))
bigrams_text = json.load(open(bigrams_text_path))

dicWords = collections.defaultdict(int)
for k, v in dictionary_freq.items():
    dicWords.setdefault(k, []).append(v)

# To identify if is word is found in the dictionary, 
# if this is found, return True, else return False to indicate the word is not found.
def isWord(word):
    status = True
    punc = string.punctuation + ' '
    if word in dicWords.keys():
        status = True
    elif word.lower() in dicWords.keys():
        status = True
    elif word in punc:
        status = True
    else:
        status = False
    return status


def add2Dict(word):
    dicWords.setdefault(word, []).append(1)  # Appending to dictionary

# get dic
def get_dic():
    return dicWords

"""
Calculate the edit distance from string 1 to string 2, e.g. from to for, needed edit distance

edit distance operation: Minimum edit distance needed to convert from to for is 3, 
that includes insertion, deletion and subsitution

From 'from'
count 1: deleted 'm'
count 2: deleted 'r'
count 3: inserted 'r' after 'o'
To 'for'

@author: team
"""
def edit_distance(str1, str2):
    m = len(str1)
    n = len(str2)
    ed = [[0 for x in range(n + 1)] for x in range(m + 1)]

    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                ed[i][j] = j
            elif j == 0:
                ed[i][j] = i
            elif str1[i - 1] == str2[j - 1]:
                ed[i][j] = ed[i - 1][j - 1]
            else:
                ed[i][j] = 1 + min(ed[i][j - 1],
                                   ed[i - 1][j],
                                   ed[i - 1][j - 1])
    return ed[m][n]


class UniSuggestion:
    def __init__(self, value, ed=1, freq=1):
        self.ed = ed
        self.freq = freq
        self.value = value


class BiSuggestion:
    def __init__(self):
        pass

# Input is a error word, check each item in dic, if edit distance <= 4, add to suggestion list
# Output is a list of UniSuggestion
def get_correct_word(w='thiis', ed=4):
    w = w
    ed = ed
    uni_suggestion_list = []
    for i in list(dicWords):
        t_ed = edit_distance(w, i)
        freq = dicWords[i][0]
        if t_ed <= ed:
            suggestion_word = UniSuggestion(i, t_ed, freq)
            uni_suggestion_list.append(suggestion_word)
    return uni_suggestion_list

# Checking real word occurance,
# the main goal from this, is to select only second word as error.
def check_real_word_occurance(sent, boolSent, index, val):
    if val: 
        return True
    else:
        if sent[index] == sent[0]:
            return False
        else:
            previous_word = boolSent[index-1]
            current_word = boolSent[index]
            # to check if current word of the first word is same as previous of the second word
            current_first_word = sent[index][0]
            previous_second_word = sent[index-1][1]
            if ( previous_word == False ) and ( current_first_word == previous_second_word ) and current_word == False:
                boolSent[index] = True
                return True
            elif previous_word == True and current_word == False:
                return False
            elif ( previous_word == False ) and ( current_first_word != previous_second_word ) and current_word == False:
                return False

#  order the correct list and return only top 5 for each edit distance
def get_ordered_correct_word(w='thiis', ed=4, limit=5):  # ed is the edit distance; limit is limit number to return
    t = get_correct_word(w=w, ed=ed)
    ordered_list = [[]]
    tmp_return_list = []
    for i in range(ed):
        ordered_list.append([])
    for item in t:
        ordered_list[(item.ed) - 1].append(item)
    for tt in range(ed):
        tmp_return_list.append(sorted(ordered_list[tt], key=lambda UniSuggestion: UniSuggestion.freq, reverse=True))
    return_list = tmp_return_list
    for i in range(len(return_list)):
        if len(tmp_return_list[i]) >= limit:
            return_list[i] = tmp_return_list[i][:limit]
        else:
            return_list[i] = tmp_return_list[i]
    return return_list

"""
Detecting Errors: Bigram probability suggestion

Approximates the probability of a word given all the previous words 

P(the|that) = P(that the) / P(that)

Main operation of this class is to:
1. Calculate bigram score 
2. Check if real word is correct

@author: team
"""    
class ErrorDetection:
    def __init__(self, sentence):
        self.bigram = sentence
        self.text = sentence

    # Converting corpus into bigram, after removal of puntuations
    def getBigram(self):
        complete_list = " ".join(str(i) for i in nlp(self.text))
        doc = nlp(complete_list)
        sentences = [sent.string.strip().lower() for sent in doc.sents]
        bigrams = [b for l in sentences for b in zip(l.split(" ")[:-1], l.split(" ")[1:])]
        bigram = [w for w in bigrams if
                  "?" not in w and ":" not in w and "," not in w and ";" not in w and "." not in w and "!" not in w]
        self.bigram = bigram

    def get_bigram_score(bigram):
        try:
            bigram_score = ErrorDetection.calculateScore(bigram)
            return bigram_score
        except:
            bigram_score = 0
            return bigram_score

    # Calculating bigram score by formula
    def calculateScore(bigram):
        freq_bigram = bigram_freq[re.sub(' ', ';', bigram)]
        freq_first_string = dictionary_freq[re.sub(' ', ';', bigram).split(";")[0]]
        score = freq_bigram / freq_first_string
        return score

    # Approximates the probability of a word given all the previous words 
    # get bigram score from original content
    # get bigram score from stemmed word
    def check_realword_error(self):
        boolErrorList = []
        for note in self.bigram:
            content = note[0] + ' ' + note[1]
            stemmed_word = " ".join(token.lemma_.strip() for token in nlp(content)) # Stemming the word
            if ErrorDetection.get_bigram_score(content) == 0:
                # real word error
                boolErrorList.append(False)
            else:
                if ErrorDetection.get_bigram_score(stemmed_word) == 0 or ErrorDetection.get_bigram_score(stemmed_word) == ErrorDetection.get_bigram_score(content):
                    boolErrorList.append(True)
                elif ErrorDetection.get_bigram_score(content) > ErrorDetection.get_bigram_score(stemmed_word) :
                    boolErrorList.append(True)
                elif ErrorDetection.get_bigram_score(content) > ( ErrorDetection.get_bigram_score(stemmed_word) * 0.01) :
                    boolErrorList.append(True)
                else:
                    boolErrorList.append(False)            

        self.text = boolErrorList

# Suggesting word based on selection.
def suggest_word(word1, word2, selection):
    def get_suggestion_List(word1, word2, selection):
        # Running on combined set dataset/bigrams_combined_set.txt
        # Running on training set dataset/bigrams_train_set.txt
        bigrams_text = json.load(open(bigrams_text_path))
        if selection == 1:
            bigram_suggestion_list_1 = []
            for i in bigrams_text:
                if i[1] == word2 and i not in bigram_suggestion_list_1:
                    bigram_suggestion_list_1.append(i)
            return bigram_suggestion_list_1

        else:
            bigram_suggestion_list_2 = []
            for i in bigrams_text:
                if i[0] == word1 and i not in bigram_suggestion_list_2:
                    bigram_suggestion_list_2.append(i)
            return bigram_suggestion_list_2

    score_list = {}
    for i in get_suggestion_List(word1, word2, selection):
        bigram_wrd = i[0] + " " + i[1]
        edit_distanc_1 = edit_distance(word1, i[0])
        edit_distanc_2 = edit_distance(word2, i[1])
        
        # display with a minimum of 10 edits distance, but keeping only top 5 of the sorted list for the word suggestion.
        # display suggested word follow by edit distance and bigram probability scores.
        if selection == 1:
            if edit_distanc_1 < 10:
                j = str(np.around(ErrorDetection.get_bigram_score(bigram_wrd), 4)) + " [" + str(edit_distanc_1) + "]"
                score_list[bigram_wrd] = edit_distanc_1
        else:
            if edit_distanc_2 < 10:
                j = str(np.around(ErrorDetection.get_bigram_score(bigram_wrd), 4)) + " [" + str(edit_distanc_2) + "]"
                score_list[bigram_wrd] = edit_distanc_2

    return score_list

#  this is for test only
if __name__ == '__main__':
    t = get_ordered_correct_word('Thiis')
    for item in t:
        for mmm in item:
            print(mmm.ed)
            print(mmm.value)
            print(mmm.freq)
        print('----------------------------------------')

