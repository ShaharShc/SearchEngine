from nltk.stem import snowball


class Stemmer:
    def __init__(self):
        self.stemmer = snowball.SnowballStemmer("english")

    def stem_term(self, token):
        """
        This function stem a token
        :param token: string of a token
        :return: stemmed token
        """
        return self.stemmer.stem(token)

    def stem_terms(self, tokens):
        after_stemming = []
        for token in tokens:
            if token[0] == '#':
                stem_token = token
            elif token == token.title():
                stem_token = self.stem_term(token).title()
            elif token.isupper():
                stem_token = self.stem_term(token).upper()
            else:
                stem_token = self.stem_term(token)
            after_stemming.append(stem_token)
        return after_stemming