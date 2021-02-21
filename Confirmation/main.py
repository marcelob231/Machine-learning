from pymongo import MongoClient
import tweepy
from datetime import date, timedelta
from keras import models
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
import numpy as np

import keys
import utils as u

NUM_WORDS = 100000
MAX_LEN = 55

model = models.load_model('model_saved')
tk = Tokenizer(num_words=NUM_WORDS, split=" ")

key_token = keys.Keys()

auth = tweepy.OAuthHandler(key_token.consu_key, key_token.consu_secret)
auth.set_access_token(key_token.acess_token, key_token.acess_secret)

api = tweepy.API(auth)

conn = MongoClient('mongodb://localhost:27017')
print(conn)
db = conn.tcc
twitter_sentiment = db.twitter_sentiment
bullies = db.bullies3

tweets_bad = twitter_sentiment.find({'sentiment': 0}, {'user_id': 1, 'name': 1, 'target': 1})

tweet_bad_list  = list(tweets_bad)

for idx,i in enumerate(tweet_bad_list):
    score_user = 0
    
    list_tweets = []
    list_dates = []
    try: 
        timeline = api.user_timeline(user_id=i['user_id'], include_rts=False, tweet_mode='extended', count=100)
    except tweepy.TweepError:
        pass
    else:
        if timeline:
            for tweet in timeline:
                if i['target'] in tweet._json['full_text']:
                    tweet._json['full_text'] = u.noemoji(tweet._json['full_text'])
                    tweet._json['full_text'] = u.cleaning(tweet._json['full_text'])
                    if tweet._json['full_text'] != "":
                        list_dates.append(tweet._json['created_at'])
                        list_tweets.append(tweet._json['full_text'])
                    
            lists_to_dic = {    
                                'tweet_text': list_tweets,
                                'created': list_dates
                            }
        else:
            lists_to_dic={}
        df = pd.DataFrame(lists_to_dic)
        num_rows = df.shape[0]  # Number of rows in the DataFrame
        if num_rows:
            print('User id: ' + i['user_id'])
            print('number of rows')
            print(num_rows)
            print('DataFrame') 
            print(df)
            X_predict = df['tweet_text']
            tk.fit_on_texts(X_predict)
            X_predict_seq = tk.texts_to_sequences(X_predict)
            X_predict_trunc = pad_sequences(X_predict_seq, maxlen=MAX_LEN)
            predictions = model.predict(X_predict_trunc)
            classes = np.argmax(predictions, axis = 1)
            df['classes'] = classes
            print('Classes: ')
            print(classes)
            df_negative = df[df['classes'] == 0]
            print('Number of classes with bad sentiment: ')
            score_user = np.count_nonzero(classes == 0)
            print(score_user)
            name = u.noemoji(i['name'])

            if score_user >= 10:
                tweet_data ={
                                'name': name,
                                'user_id': i['user_id'],
                                'target': i['target'],
                                'score': score_user,
                                'tweets': df_negative['tweet_text'].tolist()
                            }
                try:
                    bullies.insert_one(tweet_data)
                except:
                    print('Database connection error')
    print('Total users: ' + str(idx))
   
    # if idx > 30:
    #     break


