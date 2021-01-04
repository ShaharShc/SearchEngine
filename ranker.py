# you can change whatever you want in this module, just make sure it doesn't 
# break the searcher module
import math


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
        if k is not None:
            ranked_results = ranked_results[:k]
        return [d[0] for d in ranked_results]


