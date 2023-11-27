import os

import warnings
warnings.filterwarnings('ignore')

from typing import Dict
import random
import numpy as np
import pandas as pd
import tensorflow as tf

import sentencepiece as spm
from keras.models import load_model
from sklearn.ensemble import RandomForestClassifier
import sklearn 
from sklearn import ensemble, metrics
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline

import lime
from lime.lime_text import LimeTextExplainer
from lime import lime_tabular, lime_text

import matplotlib.pyplot as plt


# 텍스트 파일을 DataFrame으로 불러오기
def load_data(file_path='./src/dataset.txt'):
    df = pd.read_csv(file_path, sep='|', header=None, names=['Text', 'Label'], encoding='utf-8')
    return df


# 문장 길이 분포 확인
def analyze_sentence_length(df):
    min_len = 999
    max_len = 0
    sum_len = 0
    cleaned_corpus = list(set(df['Text']))  # set를 사용해서 중복을 제거
    print("Data Size:", len(cleaned_corpus))

    for sen in cleaned_corpus:
        length = len(sen)
        if min_len > length: min_len = length
        if max_len < length: max_len = length
        sum_len += length
    # print("문장의 최단 길이:", min_len)
    # print("문장의 최장 길이:", max_len)
    # print("문장의 평균 길이:", sum_len // len(cleaned_corpus))
    sentence_length = np.zeros((max_len), dtype=int)

    for sen in cleaned_corpus:
        sentence_length[len(sen)-1] += 1

    # plt.bar(range(max_len), sentence_length, width=1.0)
    # plt.title("Sentence Length Distribution")
    # plt.show()


# 데이터 전처리
def preprocess_data(df, max_len=60):
    filtered_corpus = [s for s in df['Text'] if (len(s) < max_len)]
    # 분포도를 다시 그려봅니다.
    sentence_length = np.zeros((max_len), dtype=int)
    for sen in filtered_corpus:
        sentence_length[len(sen)-1] += 1

    return filtered_corpus


# SentencePiece 학습
class SentencePiece:
    def __init__(self, vocab_size=8000):
        self.temp_file = os.getenv('HOME')+'/aiffel/sp_tokenizer/data/korean-english-park.train.ko.temp'
        self.vocab_size = vocab_size
    
    def train(self, corpus, model_type='unigram'):
        with open(self.temp_file, 'w') as f:
            for row in corpus:
                f.write(str(row) + '\n')
                
        spm.SentencePieceTrainer.Train(
            f'--input={self.temp_file} --model_type={model_type} --model_prefix=sp_{model_type}_{self.vocab_size} --vocab_size={self.vocab_size}'    
        )

# SentencePiece 토큰화
def sp_tokenize(s, corpus, model_name, padding='pre', max_len=40):
    tensor = list()
    # 문장을 인코딩하여 저장
    for sen in corpus:
        tensor.append(s.EncodeAsIds(sen))
        
    with open(f'./{model_name}.vocab', 'r', encoding='utf-8') as f:
        vocab = f.readlines()

    word_to_index = dict()
    index_to_word = dict()
    for idx, line in enumerate(vocab):
        word = line.split("\t")[0]
        word_to_index.update({word: idx})
        index_to_word.update({idx: word})
    # 맥스 길이 40에 맞게 패딩을 앞에 집어 넣음 padding=pre
    tensor = tf.keras.preprocessing.sequence.pad_sequences(tensor, padding=padding, maxlen=max_len)

    return tensor, word_to_index, index_to_word

# LSTM 모델 정의
def sequential_model(vocab_size, max_len=40):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Embedding(vocab_size, 1, input_shape=(max_len,)))
    model.add(tf.keras.layers.LSTM(8))
    model.add(tf.keras.layers.Dense(8, activation='relu'))
    model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    return model




# 데이터 로드 및 전처리 함수 호출
df = load_data()

# SentencePiece 토큰화
sp_model_uni_8000 = spm.SentencePieceProcessor()
sp_model_uni_8000.Load('./sp_unigram_8000.model')

# SentencePiece 토큰화 후 데이터프레임 업데이트
tensor, word_to_index, index_to_word = sp_tokenize(sp_model_uni_8000, df['Text'], f'sp_unigram_8000', max_len=60)
# df['Text'] = tensor.tolist()

# # LSTM 모델 생성 및 훈련
X_train, y_train = tensor[:4500], df['Label'][:4500]
X_val, y_val = tensor[4500:5500], df['Label'][4500:5500]
X_test, y_test = tensor[5500:], df['Label'][5500:]
# es = EarlyStopping(monitor='val_loss', patience=4, verbose=1)
# epochs = 50
# history_uni_8000 = model_uni_8000.fit(X_train, y_train, epochs=epochs, batch_size=256, callbacks=[es])
model_uni_8000 = load_model('./model_uni_8000.h5')
# model_uni_8000.summary()

# Lime
categories = df['Label'].unique()
df['Label'] = pd.Categorical(df['Label'])
df['label_code'] = df['Label'].cat.codes
class_names = df['Label'].unique()

# Split the data into training and testing sets
train_data, test_data, train_labels, test_labels = train_test_split(df['Text'], df['Label'], test_size=0.2, random_state=42)
vectorizer = TfidfVectorizer()
X_train1 = vectorizer.fit_transform(train_data)
X_test1 = vectorizer.transform(test_data)

# Random Forest 모델 생성 및 훈련
rf = RandomForestClassifier(n_estimators=500, random_state=42)
rf.fit(X_train1, train_labels) 

# 평가
# model_uni_8000로 했을때
# y_pred = model_uni_8000.predict(X_test1)
# f1 = f1_score(y_test, (y_pred > 0.5).astype(int), average='binary')
# print(f"F1 Score (LSTM): {f1}")
# y_pred_rf = rf.predict(X_test)
# f1_rf = f1_score(y_test, y_pred_rf, average='binary')
# print(f"F1 Score (Random Forest): {f1_rf}")

# RF로 했을때
pred = rf.predict(X_test1)
sklearn.metrics.f1_score(test_labels, pred, average='binary')  
c = make_pipeline(vectorizer, rf)

# LIME 설명 인스턴스 생성
explainer = LimeTextExplainer(class_names=class_names)

# LIME 설명 생성 및 시각화
idx = 2
exp = explainer.explain_instance(df['Text'].values[idx], c.predict_proba, num_features=6)
print('True class: %s' % class_names[df.Label.values[idx]])


print('Original prediction:', rf.predict_proba(X_test1[idx])[0,1])
tmp = X_test1[idx].copy()
print('Prediction removing some features:', rf.predict_proba(tmp)[0,1])
print('Difference:', rf.predict_proba(tmp)[0,1] - rf.predict_proba(X_test1[idx])[0,1])
exp.show_in_notebook(text=True)