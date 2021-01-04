import os
import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

        full_path = os.path.join(self.corpus_path, file_name)
        documents_files = []
        if file_name.endswith(".parquet"):
            df = pd.read_parquet(full_path, engine="pyarrow")
        else:
            # iterate for our root, on each directory , for her files
            for root, dirs, files in os.walk(full_path):
                for file in files:
                    if file.endswith(".parquet"):
                        full_path = os.path.join(root, file)
                        df = pd.read_parquet(full_path, engine="pyarrow")
                        documents_files.append(df)
            df = pd.concat(documents_files, sort=False)
        return df.values.tolist()

    def set_path(self, path):
        self.corpus_path = path
