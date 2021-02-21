# encoding: utf-8
from __future__ import print_function
from datetime import date, timedelta
import tweepy
from pymongo import MongoClient

import noemoji
import target_list
import keys


conn = MongoClient('mongodb://localhost:27017')
print(conn)
db = conn.tcc
twitter = db.twitter

key_token = keys.Keys()

auth = tweepy.OAuthHandler(key_token.consu_key, key_token.consu_secret)
auth.set_access_token(key_token.acess_token, key_token.acess_secret)

api = tweepy.API(auth)

def get_tweets(name, _error_mark):
    today = date.today()
    last_week = today - timedelta(days=7)
    count_tweets = 0
    try:
        for tweet in tweepy.Cursor(api.search, q=name+"-filter:retweets", lang="pt", 
                            since=last_week, tweet_mode='extended').items(300):
            count_tweets =+ 1
            tweet_data = {
                'name': noemoji.d_e(tweet._json['user']['name']),
                'user_id': tweet._json['user']['id_str'],
                'tweet_text': noemoji.d_e(tweet._json['full_text']),
                'id_tweet': tweet._json['id_str'],
                'created': tweet._json['created_at'],
                'target': name
            }
            try:
                twitter.insert_one(tweet_data)
            except:
                print('Database connection error')
        _error_mark = False
        return _error_mark
    except:
        print(name + " " + str(count_tweets))
        _error_mark = True
        return _error_mark

targets = target_list.Target_list()    

error_mark = False 
for i in targets.list_targets:
    if error_mark:
        pass
    else:
        error_mark = get_tweets(i, error_mark)

