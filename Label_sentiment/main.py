from keras import models
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
import pandas as pd
import numpy as np
from pymongo import MongoClient




NB_WORDS = 100000
MAX_LEN = 55

conn = MongoClient('mongodb://localhost:27017')
print(conn)
db = conn.tcc
twitter = db.twitter_clean
twitter_sentiment = db.twitter_sentiment

df = pd.DataFrame(list(twitter.find()))


model = models.load_model('model_saved')

tk = Tokenizer(num_words=NB_WORDS, split=" ")

X_predict = df['tweet_text']


tk.fit_on_texts(X_predict)
X_predict_seq = tk.texts_to_sequences(X_predict)
X_predict_seq_trunc = pad_sequences(X_predict_seq, maxlen=MAX_LEN)


predictions = model.predict(X_predict_seq_trunc)

classes = np.argmax(predictions, axis = 1)

df['sentiment'] = classes

print(df['sentiment'])
print(len(df['sentiment']))

df.reset_index(inplace=True)
data_dict = df.to_dict("records")

