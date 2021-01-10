# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math

#from gensim.topic_coherence.indirect_confirmation_measure import cosine_similarity
from sklearn.metrics.pairwise import cosine_similarity
from numpy.dual import norm
import numpy as np
import pandas


class Ranker:
    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, number_of_documents, relevant_inverted_docs, k=None):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param k: number of most relevant docs to return, default to everything.
        :param relevant_docs: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """

        # idx {term : [NumOfDiffDocs, {tweetID : [max_tf, repAmount, numOfUniqueWords, doc_length]}, NumOfCurrInTweetInCorpus,Cij]}
        # docs {tweetID : {term : [inverted_idx[term][tweetID], NumOfDiffDocs]}}
        Wtq2 = 0
        docs = {}
        for term in relevant_docs.keys():
            for doc in relevant_docs[term][1][1].keys():
                if doc not in docs:
                    docs[doc] = [0, 0, 0] #[cosSimilarity, inner product,normal]
            # --------------------calculate inner product-------------------
            for tweetID in relevant_docs[term][1][1].keys():
                tf = (relevant_docs[term][1][1][tweetID][1] / relevant_docs[term][1][1][tweetID][0])
                idf = (math.log2(number_of_documents / relevant_docs[term][1][0]))
                Wti = tf * idf
                Wtq = relevant_docs[term][0]
                docs[tweetID][1] += Wti * Wtq
        # -----------------------------calculate Wtq2--------------------------
        for term in relevant_docs:
            Wtq2 += relevant_docs[term][0] * relevant_docs[term][0]

        # -------------------calculate tf-idf for relevant docs-----------------
        for doc, term_dict in relevant_inverted_docs.items():
            for term, value in term_dict.items():
                idf = math.log2(number_of_documents / value[4])  # idf = log2(N/df)
                tf = value[1] / value[0]  # tf = f/max_tf
                docs[doc][2] += (idf * tf) * (idf * tf)
        # ------------------------calculate cos similarity-------------------------
        for doc in docs:
            docs[doc][0] = docs[doc][1] / (docs[doc][2] * Wtq2) ** 0.5

        ranked_results = sorted(docs.items(), key=lambda t: t[1][0], reverse=True)
        ranked_results = [d[0] for d in ranked_results]

        return ranked_results

    @staticmethod
    def rank_relevant_docs_w2v(model, relevant_docs, relevant_inverted_docs):
        docs = {}
        vec_q = Ranker.get_embedding_w2v(model, list(relevant_docs.keys()))
        norm_vec_q = norm(vec_q)
        for doc, terms in relevant_inverted_docs.items():
            vec = Ranker.get_embedding_w2v(model, list(terms.keys()))
            docs[doc] = np.dot(vec_q,vec)/(norm_vec_q*norm(vec))
        ranked_results = sorted(docs.items(), key=lambda t: t[1], reverse=True)
        #length = int(len(ranked_results)/1.8)
        #return [d[0] for d in ranked_results][:length]
        return [d[0] for d in ranked_results]

        # """for BM25"""
        # k = 1.75
        # b = 0.75
        # sum_to_average = 0
        # AVDL = 0
        # Wtq2 = 0
        # docs = {}
        # # -----------------------------calculate AVDL--------------------------
        # for doc in relevant_inverted_docs:
        #     sum_to_average += len(relevant_inverted_docs[doc])
        # AVDL = sum_to_average / len(relevant_inverted_docs)
        #
        # for term in relevant_docs.keys():
        #     for doc in relevant_docs[term][1][1].keys():
        #         if doc not in docs:
        #             docs[doc] = 0  # BM25
        #
        # for tweetID in relevant_docs[term][1][1].keys():
        #     DL = len(relevant_inverted_docs[tweetID])
        #     tf = (relevant_docs[term][1][1][tweetID][1] / relevant_docs[term][1][1][tweetID][0])
        #     idf = (math.log2(number_of_documents / relevant_docs[term][1][0]))
        #     tfStar = (tf * (k + 1)) / k * ((1 - b) + ((b * DL) / AVDL) + tf)
        #     BM25_Score = tfStar * idf
        #     if tweetID in docs:
        #         docs[doc] = BM25_Score
        #
        # ranked_results = sorted(docs.items(), key=lambda t: t[1], reverse=True)
        # r = int(len(docs))
        # ranked_results = ranked_results[:(r)]
        # return [d[0] for d in ranked_results]

    @staticmethod
    # Function returning vector reperesentation of a document
    def get_embedding_w2v(w2v_model, doc_tokens):
        embeddings = []
        if len(doc_tokens) < 1:
            return np.zeros(300)
        else:
            for tok in doc_tokens:
                if tok.lower() in w2v_model.wv.vocab:
                    embeddings.append(w2v_model.wv.word_vec(tok.lower()))
                # else:
                #     embeddings.append(np.random.rand(300))
            # mean the vectors of individual words to get the vector of the document
            return np.mean(embeddings, axis=0)

    # @staticmethod
    # def rank_relevant_docs_w2v(w2v_model, relevant_docs, relevant_inverted_docs):
    #
    #     qvector = Ranker.get_embedding_w2v(w2v_model, list(relevant_docs.keys()))
    #     tweet_id_data = {}
    #     tweet_id_CosSim = {}
    #
    #     tweet_id_data.clear()
    #     tweet_id_CosSim.clear()
    #
    #     for doc in relevant_inverted_docs:
    #         if doc not in tweet_id_data:
    #             tweet_id_data[doc] = relevant_inverted_docs[doc]
    #             tweet_id_CosSim[doc] = [0]
    #     # query_norma = 0
    #     # for value in counter_of_terms.values():
    #     #     query_norma += value ** 2
    #
    #     for key, value in tweet_id_data.items():
    #         sim = lambda x: cosine_similarity(np.array(qvector).reshape(1, -1),np.array(x).reshape(1, -1)).item()
    #         value_v = Ranker.get_embedding_w2v(w2v_model, list(value.keys()))
    #         tweet_id_CosSim[key] = sim(value_v)
    #     res = dict(sorted(tweet_id_CosSim.items(), key=lambda e: e[1], reverse=True))  # for test
    #
    #     return list(res.keys())


