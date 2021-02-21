from nltk.corpus import stopwords
import re

def cleaning(text):
    stop_words = stopwords.words("portuguese")
    
    stopchars = ['!', '.', ';', ':', ',', '>', '<', '?', '/', '"', '%', '*', '#',
    '=', '+', '(', ')', '|', '[', ']', '{', '}', '^', '$', '&', '´', '~', "'"]

    startchar = ['@', '.@', '#', '.#', 'http', '.http']

    ltext = text.lower()    #Convert sentence to lowcaps
    ntext = ltext.split()
    _ntext = []
    for word in ntext:
        check = True
        for i in startchar:             # Checks if words starts with 
            if word.startswith(i):      # characters from list startchar
                check = False
        if check:
            check2 = True
            for j in stop_words:         # Checks if word is from list stopwords 
                if word == j:           
                    check2 = False    
            if check2:
                for w in stopchars:             # Removes special characters if it's
                    word = word.replace(w, '')  # in the list stopchars 
                if word:
                    _ntext.append(word)                     # Puts word in new text list 
    sentence =" ".join(_ntext).lower()
    if sentence: 
        return sentence
    else:
        return str("")

def noemoji(text):
    regrex_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'',text)