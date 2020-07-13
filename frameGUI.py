# -*- coding: utf-8 -*-
"""
Completed:
    
    Goal: To build a spell check system by using bigram
    This python file is meant to be the Graphical user interface and where all the GUI needed functions will be in here.
    
@author: team
"""

"""
Importing Necessary library and getting the class.

@author: team
"""
# 
import wx
import re
import spacy
from collections import Counter
import numpy as np
import operator
from utils import isWord, get_ordered_correct_word, add2Dict, get_dic, ErrorDetection, suggest_word, check_real_word_occurance
from config import limit_each_ed, edit_distance, complete_tex, sentence
nlp = spacy.load('en')

"""
Getting the Frame for the GUI

@author: team
"""
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(930, 710))
        self.Center()
        self.panel = MyPanel(self)
        
class MyPanel(wx.Panel):
    def __init__(self, parent):
        super(MyPanel, self).__init__(parent)
        
        # Text Box
        self.textCtrl_input = wx.TextCtrl(self, value=sentence, size=(630, 320), style=wx.TE_MULTILINE | wx.TE_RICH2,
                                          pos=(30, 30))
        self.textCtrl_search = wx.TextCtrl(self, size=(630, 25), pos=(30, 400))
        self.textCtrl_cand = wx.TextCtrl(self, size=(260, 25), pos=(400, 480))
        
        # List Box
        self.listBox_suggestion = wx.ListBox(self, -1, (400, 550), (260, 100), [], wx.LB_SINGLE)
        self.listBox_dictionary = wx.ListBox(self, -1, (30, 480), (300, 170), [], wx.LB_SINGLE)

        # Putting label
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.label1 = wx.StaticText(self, label="Input Content:", pos=(30, 10))
        self.label2 = wx.StaticText(self, label="Search:", pos=(30, 380))
        self.label3 = wx.StaticText(self, label="Suggestions:", pos=(400, 530))
        self.label4 = wx.StaticText(self, label="Change to:", pos=(400, 460))
        self.label5 = wx.StaticText(self, label="Dictionary:", pos=(30, 460))
        self.label_remark = wx.StaticText(self, label="*red = non-word error   blue = real word error", pos=(30, 350))
        self.point = [0, 0]
        
        # Adding button
        self.btn_ignore = wx.Button(self, label="Ignore", size=(90, 35), pos=(700, 270))
        self.btn_find = wx.Button(self, label="Find", size=(90, 35), pos=(700, 400))
        self.btn_find_in_dict = wx.Button(self, label="Find in \ndictionary", size=(90, 35), pos=(800, 400))
        self.btn_check = wx.Button(self, label="Check Now", size=(87, 35), pos=(700, 320))
        self.btn_change = wx.Button(self, label="Change", pos=(700, 480))
        self.SetSizer(sizer)

        self.cboRealWord = wx.CheckBox(self, -1, "Detect real word", pos=(800,320))                 
        self.cboNonWord = wx.CheckBox(self, -1, "Detect non-word", pos=(800,340))
        self.cboRealWord.SetValue(True)
        self.cboNonWord.SetValue(True)

        # Showing tips
        self.tip_ignore = wx.ToolTip("Add to Dictionary")
        self.btn_ignore.SetToolTip(self.tip_ignore)
        self.tip_find = wx.ToolTip("Find Word to get Suggestions")
        self.btn_find.SetToolTip(self.tip_find)

        self.tip_change = wx.ToolTip("Change Now")
        self.btn_change.SetToolTip(self.tip_change)
        self.tip_suggestions = wx.ToolTip("Choose One Suggestion")
        self.listBox_suggestion.SetToolTip(self.tip_suggestions)
        self.tip_search = wx.ToolTip("Input error word to search for suggestion")
        self.textCtrl_search.SetToolTip(self.tip_search)

        # adding all listeners and events
        self.listBox_suggestion.Bind(wx.EVT_LISTBOX, self.suggestion_box_onItemSelected)
        self.btn_find.Bind(wx.EVT_BUTTON, self.insertSuggestion)
        self.btn_find_in_dict.Bind(wx.EVT_BUTTON, self.finddict)
        self.btn_change.Bind(wx.EVT_BUTTON, self.replaceContent)
        self.btn_check.Bind(wx.EVT_BUTTON, self.checkSentence)
        self.btn_ignore.Bind(wx.EVT_BUTTON, self.add2dict)
        self.textCtrl_input.Bind(wx.EVT_LEFT_UP, self.cntSelected)

        # load words from the the dictionary.
        self.load_dic()

    """
    Creating the core function such as creating dictonary, perform error detection, and 
    To provide error suggestions (based on edit distance and bigram probability)
    To provide non-word error suggestion (based on edit distance and word frequency)
    
    @author: team
    """

    # To get the text from the input content box.
    def finddict(self, event):
        tmpStr = self.textCtrl_search.GetValue().strip()
        
        if len(tmpStr) < 1:
            self.popupDlg('Please input search text')
        else:
            boolSelected = self.listBox_dictionary.SetStringSelection(tmpStr)
            if boolSelected:
                self.listBox_dictionary.SetStringSelection(tmpStr)
            else:
               self.popupDlg('Error, searched text is not found in the dictionary. Please try again.') 
               

    # Inserting necessary input from the suggestion box into box 'change'
    def suggestion_box_onItemSelected(self, event):
        index = self.listBox_suggestion.GetSelection()
        text = self.listBox_suggestion.GetString(index)
        index = text.find('[')  
        self.textCtrl_cand.Clear()
        self.textCtrl_cand.write(text[:index].rstrip())
    
    # Begin suggestion recommendations
    def insertSuggestion(self, strlist):
        self.listBox_suggestion.Clear()
        self.textCtrl_cand.Clear()
        tmpStr = self.textCtrl_search.GetValue()
    
        # When input is less than 1, prompt errors
        if len(tmpStr) < 1:
            self.popupDlg('Please input search text')
            
        # When input has 2 words, recommend words based on appropriate suggestion and recommend by edit distance and bigram probability
        elif len(tmpStr.strip().split(' ')) == 2:
            word_1 = tmpStr.strip().split(" ")[0] # Getting first word by indexing [1]
            word_2 = tmpStr.strip().split(" ")[1] # Getting second word by indexing [2]
            
            """
            Suggestion from recommending first word or second word 
            
            E.g. selection 1, gives output like chapter XX, chapter XY, chapter XZ, 
                 while selection 2, gives output like XX content, XY content, XZ content
    
            @author: team
            """
            suggestion_1 = suggest_word(word_1, word_2, 1) 
            suggestion_2 = suggest_word(word_1, word_2, 2)
            
            # To ensure {} is not empty
            if suggestion_1 != {} or suggestion_2 != {}:
                if suggestion_2 != {}:
                    suggestion_list = dict(list(suggestion_2.items()))
                    sorted_d2 = dict()
                    if suggestion_list != {}:
                        sorted_d2 = dict(sorted(suggestion_list.items(), key=operator.itemgetter(1))[:16])
                        
                    list_suggest = []
                    for i in sorted_d2:
                        if np.around(ErrorDetection.get_bigram_score(i), 4) > 0:
                            # Appending bigram score for sorting later
                            list_suggest.append([i, (str((np.around(ErrorDetection.get_bigram_score(i), 4))), str(sorted_d2[i]))])
                        
                    # Sort the bigram by descending and sort the edit distance by ascending, higher probability should be on top
                    list_suggest.sort(key=lambda item: (item[1][0]), reverse=True)
                    list_suggest.sort(key=lambda item: (item[1][1]))
                    
                    right_aligned_list = []
                    right_aligned_dict = {key.ljust(20,' '): value for key, value in list_suggest}
                    
                    # To ensure word is with 4 decimal places
                    for key, value in right_aligned_dict.items():
                        prob_number = float(value[0])
                        prob = f"{prob_number:2,.4f}"
                        right_aligned_list.append(key + ' [' + value[1] + '] ' + str(prob))
        
                    # Appending suggestions to the list box
                    for item in right_aligned_list[:10]:
                        self.listBox_suggestion.Append(item)
                
                elif suggestion_1 != {}:
                    suggestion_list = dict(list(suggestion_1.items()))
                    sorted_d2 = dict()
                    if suggestion_list != {}:
                        sorted_d2 = dict(sorted(suggestion_list.items(), key=operator.itemgetter(1))[:16])
                        
                    list_suggest = []
                    for i in sorted_d2:
                        if np.around(ErrorDetection.get_bigram_score(i), 4) > 0:
                            list_suggest.append([i, (str((np.around(ErrorDetection.get_bigram_score(i), 4))), str(sorted_d2[i]))])
                            #print([i, (str((np.around(ErrorDetection.get_bigram_score(i), 4))), str(sorted_d1[i]))])
                        
                    # Sort the bigram by descending and sort the edit distance by ascending, higher probability should be on top
                    list_suggest.sort(key=lambda item: (item[1][0]), reverse=True)
                    list_suggest.sort(key=lambda item: (item[1][1]))
                    
                    right_aligned_list = []
                    right_aligned_dict = {key.ljust(20,' '): value for key, value in list_suggest}
                    
                    # To ensure word is with 4 decimal places
                    for key, value in right_aligned_dict.items():
                        prob_number = float(value[0])
                        prob = f"{prob_number:2,.4f}"
                        right_aligned_list.append(key + ' [' + value[1] + '] ' + str(prob))
        
                    for item in right_aligned_list[:10]:
                        self.listBox_suggestion.Append(item)
            else:
                # Prompt error as no suggestion is appeared in the dictionary
                self.popupDlg('No suggestion suggested.')
    
        # USer has selected more than 2 words, prompt error to have enough input
        elif len(tmpStr.strip().split(' ')) > 2:
            self.popupDlg('Select too much, only 2 words please')
    
        # This is assume user key in 1 word, so the developer to ensure it runs dictionary lookup.
        else:
            strlist = get_ordered_correct_word(tmpStr.lower().strip(), edit_distance, limit_each_ed)
            sum = 0
            for i in strlist:
                sum = sum + len(i)
            if sum < 1:
                self.listBox_suggestion.Append('There is no suggestion, please add to dic.')
            else:
                for item in strlist:
                    if len(item) == 0:
                        print('this should not be added')
                    else:
                        self.listBox_suggestion.Append('Edit distance: ' + str(strlist.index(item) + 1) + '  ******')
                        for mmm in item:
                            t1 = mmm.value + '     [' + str(mmm.freq) + ']'
                            self.listBox_suggestion.Append(t1)
    
    
    # Flag the non-word error from black text color to red text color.
    def changeContentColor(self, startPoint, endPoint):
        startPoint = startPoint
        endPoint = endPoint
        points = self.textCtrl_input.GetFont().GetPointSize()
        # Creating new text font
        f = wx.Font(points + 2, wx.ROMAN, wx.ITALIC, wx.BOLD, True)
        # To ensure only selected non-word is being highlighted /flagged
        self.textCtrl_input.SetStyle(startPoint, endPoint, wx.TextAttr("red", wx.NullColour, f))
    
    # Flag the real word error from black text color to blue text color.
    def changeContentColor2(self, startPoint, endPoint):
        startPoint = startPoint
        endPoint = endPoint
        points = self.textCtrl_input.GetFont().GetPointSize()
        # Creating new text font
        f = wx.Font(points + 2, wx.ROMAN, wx.ITALIC, wx.BOLD, True)
        # To ensure only selected non-word is being highlighted /flagged
        self.textCtrl_input.SetStyle(startPoint, endPoint, wx.TextAttr("blue", wx.NullColour, f))
    
    # Reseting text color back to black.
    def resetContentColor(self, start, end):
        f = self.textCtrl_input.GetFont()
        self.textCtrl_input.SetStyle(start, end, wx.TextAttr("black", wx.NullColour, f))
    
    # Replace errors from the context
    def replaceContent(self, content):
        content = self.textCtrl_cand.GetValue()
        if len(content) > 0:
            start = self.point[0]
            end = self.point[1]
            self.textCtrl_input.Replace(start, end, (content.rstrip() + ' '))
        else:
            # Validate if user does not key input
            self.popupDlg('Please input text to be changed.')
            
    # texts will be placed into box 'find' once the user highlight texts from the content box. Key Up listener is used. 
    # in order to perform non-word and real-word suggestion recommendation.
    def cntSelected(self, event):
        point = self.textCtrl_input.GetSelection()
        self.point[0] = point[0]
        self.point[1] = point[1]
        tmpStr = self.textCtrl_input.GetStringSelection()
        # add selected string to search input
        self.textCtrl_search.Clear()
        self.textCtrl_search.AppendText(tmpStr.strip())
    
    # Allow flexibility to serach real word only, non-word error only or both non word and real word errors at the same time.
    # Non-word errors found will be set to red text, while real word errors will be set to blue text.
    def checkSentence(self, event):
        valuelist = list()
        valuelist.append(self.cboRealWord.GetValue())
        valuelist.append(self.cboNonWord.GetValue())
        tmpStr = self.textCtrl_input.GetValue() # getting input string from textCtrl
    
        # if text does not have more than 1 input content, prompt error.
        if len(tmpStr) < 1:
            self.popupDlg('Please input content')
        else:
            # If user does not select any errors to be detected.
            if valuelist[0] == False and valuelist[1] == False:
                # prompt error message
                self.popupDlg('Please select checkbox button.')
                sentence = self.textCtrl_input.GetValue()
                
                start = 0
                end = len(sentence)
                self.resetContentColor(start, end)
                
            # User selected both real word and non-word error to be detected.
            elif valuelist[0] == True and valuelist[1] == True:
                sentence = self.textCtrl_input.GetValue() # Get the string input
        
                start = 0
                end = len(sentence)
                self.resetContentColor(start, end) # Reset to black text
                
                #  check real-word error
                error = ErrorDetection(sentence)
                error.getBigram()
                error.check_realword_error()
                
                sent = error.bigram
                boolSent = error.text
                result_list = []
                if boolSent != None or boolSent != []:
                    for index , val in enumerate(boolSent):
                        boolresult = check_real_word_occurance(sent, boolSent, index, val)
                        result_list.append(boolresult)       
                        
                    result = [x for x, y in zip(sent, result_list) if y is False]
                    for i in result:
                        firstword = nlp(i[0])
                        secondword = nlp(i[1])
                        boolResult = isWord([i.text for i in firstword][0]) and isWord([i.text for i in secondword][0])
                        
                        """
                        Flag the word
            
                        if result is found not to be a non-word error but is a real word error,  
                            the developer will flag the error as real word error and text will be changed to blue.
                        
                        In order word, if it is found to be a non-word error and is a real word error at the same time,
                            system will choose to ignore it, and will pass to non-word checker to change the text to red.
    
                        @author: team
                        """
                                               
                        if boolResult:
                            String = sentence
                                
                            bigram_first_word = i[0]
                            bigram_second_word = i[1]
                                
                            Substring = bigram_first_word + ' ' + bigram_second_word
                            x = re.search(Substring, String, re.IGNORECASE)
                            if x != None:
                                self.changeContentColor2(x.span()[0], x.span()[1]) # x.span()[0] + len(i[0]) + 1, x.span()[1])
                        
                #  check non-word error
                doc = nlp(sentence)
                for i in doc:
                    tmp = i.text
                    if not (isWord(tmp)):  # if word is not found in the dictionary, it will be consider as non-word error, the developer will flag as red text
                        all_list_point = [m.start() for m in re.finditer(re.compile(r"\b(%s)\b" %tmp), sentence)]
                        for start_point in all_list_point:
                            start = start_point
                            end = start + len(tmp)
                            self.changeContentColor(start, end)
    
            # User selected to detect non-word error
            elif valuelist[0] == False and valuelist[1] == True:
                # Nonword error only
                sentence = self.textCtrl_input.GetValue()
                
                start = 0
                end = len(sentence)
                self.resetContentColor(start, end) # reset context into black
                
                doc = nlp(sentence)
                for i in doc:
                    tmp = i.text
                    if not (isWord(tmp)):  # if word is not found in the dictionary, it will be consider as non-word error, the developer will flag as red text
                        # Getting the non-word error indexes (to indicate the position of non-word error)
                        all_list_point = [m.start() for m in re.finditer(re.compile(r"\b(%s)\b" %tmp), sentence)]
                        for start_point in all_list_point:
                            start = start_point
                            end = start + len(tmp)
                            self.changeContentColor(start, end) # Flag non-word error as red text
            
            # User selected to detect real word error only.
            elif valuelist[0] == True and valuelist[1] == False:
                # Real word error only
                sentence = self.textCtrl_input.GetValue()
                start = 0
                end = len(sentence)
                self.resetContentColor(start, end) # Reset content to black
                
                # Detect real word error, creating a class to convert context to bigram and calculate the score.
                error = ErrorDetection(sentence)
                error.getBigram()
                error.check_realword_error()
                
                sent = error.bigram
                boolSent = error.text
                result_list = []
                if boolSent != None or boolSent != []:
                    for index , val in enumerate(boolSent):
                        boolresult = check_real_word_occurance(sent, boolSent, index, val)
                        result_list.append(boolresult)       
                        
                    result = [x for x, y in zip(sent, result_list) if y is False]
                    for i in result:
                        String = sentence
                        
                        bigram_first_word = i[0]
                        bigram_second_word = i[1]
                        
                        Substring = bigram_first_word + ' ' + bigram_second_word
                        x = re.search(Substring, String, re.IGNORECASE)
                        if x != None:
                            self.changeContentColor2(x.span()[0], x.span()[1]) # Flag as blue text
                            
    # To ignore text that is found to be errors, only highlighted text will be reflected.
    # Logic is to add the errors into dictionary list temporary, to ignore text at the time being.
    def add2dict(self, event):
        tmpStr = self.textCtrl_search.GetValue()
        if tmpStr:
            add2Dict(tmpStr)
            self.load_dic()
            # change word color to normal color after adding to dictionary
            all_list_point = [m.start() for m in re.finditer(tmpStr, sentence)]
            for start_point in all_list_point:
                start = start_point
                end = start + len(tmpStr)
                self.resetContentColor(start, end)
        self.checkSentence(event)
    
    # Load the dictionary into the list box from the corpus
    def load_dic(self):
        dic_words = get_dic()
        # sort the dictionary, add to dic list
        for w in sorted(dic_words.keys()):
            self.listBox_dictionary.Append(w)
    
    # populate dialog messages
    def popupDlg(self, msg):
        dlg = wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)


class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None, title="Spell Check System")
        self.frame.Show()
        return True


if __name__ == '__main__':
    app = MyApp()
    app.MainLoop()
