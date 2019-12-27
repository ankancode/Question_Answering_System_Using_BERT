import nltk
import re
import wikipedia
import spacy
from spacy import displacy
import en_core_web_sm
from bert import QA
from nltk.corpus import stopwords
import os
from nltk.tokenize import RegexpTokenizer


def wiki_search(search_phrase):

    tokenizer = RegexpTokenizer(r'\w+')
    phrase_tokens = nltk.word_tokenize(search_phrase.lower())
    phrase_len = len(phrase_tokens)
    all_related_phrases = []
    flag = False
    
    try:
        page = wikipedia.page(search_phrase.capitalize())
    except wikipedia.exceptions.DisambiguationError as e:
        all_related_phrases = e.options
    except wikipedia.exceptions.PageError as e:
        return 

    if all_related_phrases==[]:
        all_related_phrases = wikipedia.search(search_phrase.capitalize())
    
    all_related_phrases_relevant = []
    
    for phrase in all_related_phrases:
        alternative_phrase_tokens = nltk.word_tokenize(phrase.lower())
        flag = set(phrase_tokens).issubset(set(alternative_phrase_tokens))
        if flag:
            all_related_phrases_relevant.append(phrase)

    all_events = []

    if all_related_phrases_relevant != []:
        
        for i in all_related_phrases_relevant:
            i = tokenizer.tokenize(i)
            i = '-'.join(i[::-1])

            try:
                data = wikipedia.page(i.capitalize()).content
            except:
                continue
            
            required_data, _ , _ = data.partition('== See also ==')
            required_data = nltk.sent_tokenize(required_data)
            events = [line.rstrip() for line in required_data] 
            cleaned_events = []
            for line in events:
                if line:
                    line = line.replace('\n', ' ')
                    # cleaned_events.append(re.sub(r'=[0-9a-zA-Z_\D]*=', r'', line))
                    cleaned_events.append(line)
            all_events.extend(cleaned_events)
                
    else:
        return []

    return all_events


def get_model_api():
    
    model = QA('model')
    nlp = en_core_web_sm.load()
    stop_words = set(stopwords.words('english'))
   
    def model_api(question):
        try :
            question = [w.capitalize() for w in question.split(" ")]
            question = " ".join(question)
            doc = nlp(question)
            search = []
            
            for chunk in doc.noun_chunks:
                query = chunk.text
                check_query = nlp(query.lower())
    
                if 'PROPN' in [token.pos_ for token in check_query ]:
                    querywords = query.split()
                    query_sentence = [w.lower() for w in querywords if not w.lower() in stop_words] 
                    query_sentence = ' '.join(query_sentence)
                    search.append(query_sentence)

            search = [w for w in search if w!='']
            print(search)
            
            all_content = ''
            if len(search) != 0 :
                for i in search:
                    i = [w.capitalize() for w in i.split(" ")]
                    i = " ".join(i)
                    
                    for j in wiki_search(i.capitalize()):
                        all_content = all_content + j + '.'

            answer = model.predict(all_content, question)

            return answer['answer']
            
        except:
            return "Sorry, I don't know, can you be a bit more specific OR Wikipedia Server is Busy so can't get Response ."
    
    return model_api
    


