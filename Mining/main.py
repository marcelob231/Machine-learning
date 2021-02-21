import pandas as pd
import numpy as np
import collections
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedKFold
from keras.preprocessing.sequence import pad_sequences
from keras.utils.np_utils import to_categorical
from keras.preprocessing.text import Tokenizer
from sklearn.preprocessing import LabelEncoder
from keras import models
from keras import layers
from pymongo import MongoClient
import time

import utils as u

NUM_WORDS = 100000  
NUM_EPOCHS = 4  
BATCH_SIZE = 256  
MAX_LEN = 55
NUM_FOLDS = 10

start_time = time.time()

df = pd.read_csv('Train500.csv', sep=';', encoding='utf-8')
size_sample = len(df.index)
df = df.sample(n=size_sample)
df = df.reset_index(drop=True)
df['tweet_text'] = df['tweet_text'].apply(u.cleaning).apply(u.noemoji)

df.to_pickle("train500_clean.pkl")

skf = StratifiedKFold(n_splits=NUM_FOLDS, shuffle=True)
skf.get_n_splits(df.tweet_text, df.sentiment)

for train_index, test_index in skf.split(df.tweet_text, df.sentiment):
    X_train, X_test = df.tweet_text[train_index], df.tweet_text[test_index]
    y_train, y_test = df.sentiment[train_index], df.sentiment[test_index]

    tk = Tokenizer(num_words=NUM_WORDS, split=" ")

    tk.fit_on_texts(X_train)
    X_train_seq = tk.texts_to_sequences(X_train)
    X_test_seq = tk.texts_to_sequences(X_test)

    X_train_maxlen = pad_sequences(X_train_seq, maxlen=MAX_LEN)
    X_test_maxlen = pad_sequences(X_test_seq, maxlen=MAX_LEN)

    label = LabelEncoder()
    y_train_label = label.fit_transform(y_train)
    y_test_label = label.transform(y_test)
    y_train_oh = to_categorical(y_train_label)
    y_test_oh = to_categorical(y_test_label)

    X_train_emb, X_valid_emb, y_train_emb, y_valid_emb = \
        train_test_split(X_train_maxlen, y_train_oh, test_size=0.1, random_state=37)

    start_time = time.time()

    emb_model = models.Sequential()
    emb_model.add(layers.Embedding(NUM_WORDS, 8, \
        input_length=MAX_LEN))
    emb_model.add(layers.Flatten())
    emb_model.add(layers.Dense(2, activation='softmax'))
    emb_model.summary()

    emb_model.compile(optimizer='rmsprop', \
        loss='categorical_crossentropy', metrics=['accuracy'])
    emb_model_result = emb_model.fit(X_train_emb, y_train_emb, \
        epochs=NUM_EPOCHS, batch_size=BATCH_SIZE, \
            validation_data=(X_valid_emb, y_valid_emb), verbose=2)
    emb_model.save('model_saved')

    print("Time taken for trainning model: " + str(time.time() - start_time))
