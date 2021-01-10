class ConfigClass:
    def __init__(self):
        # link to a zip file in google drive with your pretrained model
        #TODO check if the url is correct
        self._model_url = 'https://drive.google.com/file/d/10bHPWa6gFUEXKgOfp61qL0N9r3-FnREs/view?usp=sharing'
        # False/True flag indicating whether the testing system will download 
        # and overwrite the existing model files. In other words, keep this as 
        # False until you update the model, submit with True to download 
        # the updated model (with a valid model_url), then turn back to False 
        # in subsequent submissions to avoid the slow downloading of the large 
        # model file with every submission.
        self._download_model = True

        self.corpusPath = ''
        # TODO change the inverted index file name before summbit and save the idx_bench.pkl
        self.saveInvertedPath = 'idx_bench.pkl'
        self.savedFileMainFolder = ''
        self.saveFilesWithStem = self.savedFileMainFolder + "WithStem"
        self.saveFilesWithoutStem = self.savedFileMainFolder + "WithoutStem"
        self.toStem = False

        print('Project was created successfully..')

    def get__corpusPath(self):
        return self.corpusPath

    def get__savedFileMainFolder(self):
        return self.savedFileMainFolder

    def get_model_url(self):
        return self._model_url

    def set_download_model(self, bool):
        self._download_model = bool

    def get_download_model(self):
        return self._download_model

    def get_saveInvertedPath(self):
        return self.saveInvertedPath
