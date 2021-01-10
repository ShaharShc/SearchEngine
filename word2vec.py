import logging
import pickle
from time import time  # To time our operations
import multiprocessing

import gensim
from gensim.models import Word2Vec

class BuildingModel:
    def __init__(self):
        self.model = ''

    def training(self):
        with open('all_corpus.pkl', 'rb') as f:
            sentences = pickle.load(f)
        f.close()

        new_sentences = []
        for sentence in sentences:
            new_sentence = []
            for word in sentence:
                if " " in word or word[0] == "#" or word[0] == '@':
                    continue
                else:
                    new_sentence.append(word)
            new_sentences.append(new_sentence)


        cores = multiprocessing.cpu_count()  # Count the number of cores in a computer

        w2v_model = Word2Vec(min_count=10,
                         window=2,
                         size=300,
                         sample=6e-5,
                         alpha=0.03,
                         min_alpha=0.0007,
                         negative=20,
                         workers=cores - 1,
                         sg=1)
        t = time()

        w2v_model.build_vocab(new_sentences, progress_per=10000)

        print('Time to build vocab: {} mins'.format(round((time() - t) / 60, 2)))

        t = time()

        w2v_model.train(sentences, total_examples=w2v_model.corpus_count, epochs=10, report_delay=1)

        print('Time to train the model: {} mins'.format(round((time() - t) / 60, 2)))

        w2v_model.init_sims(replace=True)

        w2v_model.wv.save_word2vec_format('trained_w2v_model',binary=True)
        self.model = w2v_model




