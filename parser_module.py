import collections
import json
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
from document import Document
import re

class Parse:

    def __init__(self):
        # self.stop_words = frozenset(stopwords.words('english'))
        self.stop_words = stopwords.words('english')
        self.my_stop_words = {'_', "'", '\n', '\t', '.', ' ', '', '(', ')', ',', '*', ':', ';', '-', '|', '#', '—', '?','!', '$', '+', '&', '/', '<', '>', '=', '@', '[', ']', '^', '`', '{', '}', '~', '"'}
        self.percent_dic = {'percent', 'percentage', '%'}
        self.dollar_dic = {'$', 'dollar', 'dollars'}
        self.K_M_B = {'thousand', 'k', 'million', 'mill', 'm', 'milli', 'billion', 'b'}

    def parse_sentence(self, text, url):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        tweet_tokenizer = TweetTokenizer()
        text_tokens = tweet_tokenizer.tokenize(text)

        new_text_tokens = []
        List_of_entity = []
        entity_tokens = []
        strudel_list = []

        if len(text_tokens) > 0:
            for token in text_tokens:
                if token == 'RT':
                    continue
                if self.GetEntitiesAndNames(entity_tokens, token, List_of_entity):
                    List_of_entity = []
                if len(token) == 1 and not token.isdigit():
                    continue
                if token.find("https") != -1:
                    continue
                if all(ord(char) < 128 for char in token) == False:
                    continue
                if token in self.my_stop_words or token.lower() in self.stop_words:
                    continue
                elif all(char in self.my_stop_words for char in token):
                    continue
                elif token[0] == '@':
                    strudel_list.append(token)
                    continue
                if self.numeric_word(token) is not False:
                    token = self.numeric_word(token)
                number = token.replace(',', '')
                if len(token) > 1 and token[0] == '#':
                    connected_word = self.parse_hashtag(token, new_text_tokens)
                    new_text_tokens.append('#' + connected_word)
                elif token.lower() in self.percent_dic or token.lower() in self.K_M_B:
                    self.parse_before_number(token, new_text_tokens)
                elif number.isnumeric() or self.is_fractional(number):
                    self.parse_contain_num(number, new_text_tokens)
                # separate word by Punctuation
                elif not token.isalpha() and token[0] != '@' and token[0] != '#':
                    split = self.split_word(token)
                    check_split, connected_split = self.parse_split(split)
                    new_text_tokens.extend(check_split)
                else:
                    new_text_tokens.append(token)

        extend_url = self.check_url(url)
        if extend_url is not None:
            new_text_tokens.append(extend_url)

        # dict of terms - upper case lower case taking care
        term_dict = self.TakeCareOfCases(new_text_tokens)

        tokens = []
        for term in term_dict.keys():
            for i in range(term_dict[term]):
                tokens.append(term)

        if len(strudel_list) > 1:
            tokens.extend(strudel_list)
        elif len(strudel_list) == 1:
            tokens.append(strudel_list[0])

        if len(entity_tokens) > 1:
            tokens.extend(entity_tokens)
        elif len(entity_tokens) == 1:
            tokens.append(entity_tokens[0])

        return tokens

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        if doc_as_list[3] is None or doc_as_list[3] == '{}':
            url = None
        else:
            url = json.loads(doc_as_list[3])
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        if doc_as_list[6] is None or doc_as_list[6] == '{}':
            retweet_url = None
        else:
            retweet_url = json.loads(doc_as_list[6])
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        if doc_as_list[9] is None or doc_as_list[9] == '{}':
            quote_url = None
        else:
            quote_url = json.loads(doc_as_list[9])
        quote_indices = doc_as_list[10]
        retweet_quote_text = doc_as_list[11]
        retweet_quote_indices = doc_as_list[12]


        # check_RT = full_text[:2]
        # if check_RT == 'RT':
        #     return None

        tokenized_text = self.parse_sentence(full_text, url)
        doc_length = len(tokenized_text)  # after text operations.

        #dict of all terms (after stemming if true + entities)
        term_dict = dict(collections.Counter(x for x in tokenized_text if x))

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)

        return document

    def check_url(self, url):
        if url is not None:
            for val in url.values():
                if val is not None:
                    if 'twitter.com' in val:
                        return None
                    extend_url = re.split("[: / = ? - % + _ -]", val)
                    extend_url = [w for w in extend_url if w not in self.stop_words and w not in self.my_stop_words]
                    for u in extend_url:
                        if u.__contains__('.'):
                            if u.startswith('www.'):
                                u = u.replace('www.', '')
                            return u.lower()
        else:
            return None

    def parse_split(self, check):
        after_chek = []
        connect = ''
        for c in check:
            if self.numeric_word(c) is not False:
                c = self.numeric_word(c)
            number = c
            number = number.replace(',', '')
            if len(c) == 1 and not c.isdigit():
                continue
            if c in self.my_stop_words:
                continue
            elif c.lower() in self.percent_dic:
                self.parse_percent(after_chek)
            elif c.lower() in self.percent_dic or c.lower() in self.K_M_B:
                self.parse_before_number(c, after_chek)
            elif number.isnumeric() or self.is_fractional(number):
                self.parse_contain_num(number, after_chek)
            else:
                after_chek.append(c)
            connect += c
        return after_chek, connect

    def parse_before_number(self, token, new_text_tokens):
        if token.lower() in self.percent_dic:
            self.parse_percent(new_text_tokens)
        elif token.lower() in self.K_M_B:
            self.parse_K_M_B(token, new_text_tokens)


    def parse_contain_num(self, number, new_text_tokens):
        if number.isnumeric():
            if len(new_text_tokens) != 0 and new_text_tokens[len(new_text_tokens) - 1] in self.dollar_dic:
                self.parse_dollar(new_text_tokens, number)
            else:
                self.parse_number(number, new_text_tokens)

        elif self.is_fractional(number):
            self.parse_fractional(number, new_text_tokens)

    def parse_hashtag(self, token_from_text, new_text_tokens):
        token = token_from_text[1:]
        new_token = []

        if token.isalpha() and (token.islower() or token.isupper()):
            new_token = token

        elif not token.isalpha():
            check = self.split_word(token)
            for i in range(len(check)):
                if check[i].isnumeric():
                    self.parse_number(check[i], new_token)
                elif check[i].isalpha() and check[i].islower() is False and check[i].isupper() is False:
                    myString = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', check[i])
                    new_token.extend(myString.split())
                else:
                    new_token.append(check[i])

        elif token.isalpha() and token.islower() is False and token.isupper() is False:
            myString = re.sub(r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))', r' \1', token)
            new_token = myString.split()

        if len(new_token) > 1 and type(new_token) is list:
            after_parse_split, connect_word = self.parse_split(new_token)
            new_text_tokens.extend([x.lower() for x in after_parse_split if x != ''])
            return connect_word.lower()

        else:
            new_text_tokens.append(token.lower())
            return token.lower()

    # split word if alpha or not
    def split_word(self, wordToSplit):
        new_word = []
        eow_index = -1  # End of word index
        for i, char in enumerate(wordToSplit):
            if i == len(wordToSplit):
                break
            if i < eow_index:
                continue
            word = []
            if char.isalpha():
                while i != len(wordToSplit) and wordToSplit[i].isalpha():
                    word.append(wordToSplit[i])
                    i += 1
                eow_index = i
                new_word.append(''.join(word))
            elif char.isdigit():
                while i != len(wordToSplit) and wordToSplit[i].isdigit():
                    word.append(wordToSplit[i])
                    i += 1
                eow_index = i
                new_word.append(''.join(word))
            elif char == '%':
                new_word.append(char)
            else:
                continue
        return new_word

    def parse_dollar(self, new_text_tokens, token):
        last_token_index = len(new_text_tokens) - 1
        new_text_tokens[last_token_index] = '$' + token

    def parse_percent(self, new_text_tokens):
        last_token_index = len(new_text_tokens) - 1
        if last_token_index >= 0:
            check_number = new_text_tokens[last_token_index]
            if check_number.isnumeric():
                percent_term = check_number + "%"
                new_text_tokens[last_token_index] = percent_term

    def parse_K_M_B(self, token, new_text_tokens):
        thousand = {'thousand', 'k'}
        million = {'million', 'mill', 'm', 'milli'}
        billion = {'billion', 'b'}

        last_token_index = len(new_text_tokens) - 1
        if last_token_index >= 0:
            number = new_text_tokens[last_token_index]
            if number.isnumeric():
                if token.lower() in thousand:
                    new_token = number + 'K'
                    new_text_tokens[last_token_index] = new_token
                elif token.lower() in million:
                    new_token = number + 'M'
                    new_text_tokens[last_token_index] = new_token
                elif token.lower() in billion:
                    new_token = number + 'B'
                    new_text_tokens[last_token_index] = new_token

    def numeric_word(self, token):
        num_dic = {'zero': '0',
                   'one': '1',
                   'two': '2',
                   'three': '3',
                   'four': '4',
                   'five': '5',
                   'six': '6',
                   'seven': '7',
                   'eight': '8',
                   'nine': '9',
                   'ten': '10',
                   'eleven': '11',
                   'twelve': '12',
                   'thirteen': '13',
                   'fourteen': '14',
                   'fifteen': '15',
                   'sixteen': '16',
                   'seventeen': '17',
                   'eighteen': '18',
                   'nineteen': '19',
                   'twenty': '20',
                   'thirty': '30',
                   'forty': '40',
                   'fifty': '50',
                   'sixty': '60',
                   'seventy': '70',
                   'eighty': '80',
                   'ninety': '90',
                   'hundred': '100', }

        if token not in num_dic:
            return False
        else:
            return num_dic[token]

    def is_fractional(self, s):
        if len(s) == 3:
            if s[0].isnumeric() and s[1] == '/' and s[2].isnumeric():
                return True
        return False

    def parse_fractional(self, number, new_text_tokens):
        last_token_index = len(new_text_tokens) - 1
        if last_token_index >= 0:
            p_number = new_text_tokens[last_token_index]
            if p_number.isnumeric():
                new_text_tokens[last_token_index] = p_number + ' ' + number

    def parse_number(self, number, new_text_tokens):
        str_num = number
        number = float(number)
        if number < 1000:
            if number - int(number) != 0:
                index_p = str_num.find('.')
                number = str_num[:index_p + 4]
            else:
                number = int(number)
            new_text_tokens.append(str(number))

        elif 999 < number < 1000000:
            token = self.put_K_M_B('K', 1000, number, 0, 1, 2)
            new_text_tokens.append(token)

        elif 999999 < number < 1000000000:
            token = self.put_K_M_B('M', 1000000, number, 3, 4, 5)
            new_text_tokens.append(token)

        elif 999999999 < number < 1000000000000:
            token = self.put_K_M_B('B', 1000000000, number, 6, 7, 8)
            new_text_tokens.append(token)

    def get_pos_nums(self, num):
        pos_nums = []
        while num != 0:
            pos_nums.append(num % 10)
            num = num // 10
        return pos_nums

    def put_K_M_B(self, K_M_B, num_type, number, one, two, three):
        number = int(number)
        num_position = self.get_pos_nums(number)

        if num_position[one] != 0:
            new_num = str(int(number / num_type)) + '.' + str(num_position[three]) + str(num_position[two]) + str(
                num_position[one]) + K_M_B
            return new_num
        else:
            if num_position[two] != 0:
                new_num = str(int(number / num_type)) + '.' + str(num_position[three]) + str(num_position[two]) + K_M_B
                return new_num
            else:
                if num_position[2] != 0:
                    new_num = str(int(number / num_type)) + '.' + str(num_position[three]) + K_M_B
                    return new_num
                else:
                    new_num = str(int(number / num_type)) + K_M_B
                    return new_num

    # adding entities to the list
    def GetEntitiesAndNames(self, entity_tokens, term, List_of_entity):
        List_of_elements_to_end_entity = self.my_stop_words
        List_of_elements_to_end_entity.union(self.percent_dic)
        List_of_elements_to_end_entity.union(self.dollar_dic)
        List_of_elements_to_end_entity.union(self.K_M_B)
        CLterm = term
        CLterm = CLterm.capitalize()
        if all(ord(char) < 128 for char in term) and term == CLterm and term.isalpha() and term.lower() not in List_of_elements_to_end_entity :
            # start taking words to create entity/name
            List_of_entity.append(term)
        elif len(List_of_entity) > 1 and (term.islower() or term.isupper() or term.lower() in List_of_elements_to_end_entity or not term[0].isalpha() or not all(ord(char) < 128 for char in term)):
            entity_tokens.append(' '.join(List_of_entity))
            return True
        elif len(List_of_entity) == 1 and (term.islower or term.isupper or term.lower() in List_of_elements_to_end_entity or not term[0].isalpha() or not all(ord(char) < 128 for char in term)):
            return True
        return False

    # making a dict of terms - chars upper or lower
    def TakeCareOfCases(self, text_tokens):
        term_dict = {}
        for term in text_tokens:
            if term.isalpha():
                if term in term_dict.keys():
                    term_dict[term] += 1
                else:
                    upterm= term.upper()
                    lowterm = term.lower()
                    if term[0].islower():
                        if upterm in term_dict:
                            if lowterm in term_dict:
                                term_dict[lowterm] += term_dict.pop(upterm) + 1
                            else:
                                term_dict[lowterm] = term_dict.pop(upterm) + 1
                        elif lowterm in term_dict:
                            term_dict[lowterm] += 1
                        else:
                            term_dict[lowterm] = 1
                    elif term[0].isupper():
                        if upterm in term_dict:
                            term_dict[upterm] += 1
                        elif lowterm in term_dict:
                            term_dict[lowterm] += 1
                        else:
                            term_dict[upterm] = 1
            else: # non-words
                if term in term_dict.keys():
                    term_dict[term] += 1
                else:
                    term_dict[term] = 1
        return term_dict

