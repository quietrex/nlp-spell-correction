# -*- coding: utf-8 -*-
"""
Completed by team: main.py
    
    Goal: To build a spell check system by using bigram
    This python file is meant to be config file, all the training set and training set + validation set (combined set files) will be here!
    To increase code reusability by setting up recallable variables.
    
@author: team
"""
# Setting the training set path
# Training set
#dic_path = "dataset/dictionary_freq_trainset.txt"
#bigram_freq_path = "dataset/bigram_freq_trainset.txt"
#bigrams_text_path = "dataset/bigrams_train_set.txt"

# Validation and training set combined
dic_path = "dataset/dictionary_freq_combinedset.txt"
bigram_freq_path = "dataset/bigram_freq_combined_set.txt"
bigrams_text_path = "dataset/bigrams_combined_set.txt"

limit_each_ed = 5
edit_distance = 4

# Test Sentences
complete_tex = "The potential. Thiis processes? I has highlighted. a overview of pen."
sentence = ""

