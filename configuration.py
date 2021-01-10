class ConfigClass:
    def __init__(self):
        # link to a zip file in google drive with your pretrained model
        #TODO check if the url is correct
        self._model_url = 'https://drive.google.com/file/d/1PNTo2mvScBt2eNgfzfsvFKpasjyankmk/view?usp=sharing'
        # False/True flag indicating whether the testing system will download 
        # and overwrite the existing model files. In other words, keep this as 
        # False until you update the model, submit with True to download 
        # the updated model (with a valid model_url), then turn back to False 
        # in subsequent submissions to avoid the slow downloading of the large 
        # model file with every submission.
        #TODO change before sumbit
        #self._download_model = True
        self._download_model = False

        self.corpusPath = ''
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

    def set_saveFilesWithoutStem(self, fn):
        self.saveFilesWithoutStem += "\\" + fn

    def get_saveFilesWithoutStem(self):
        return self.saveFilesWithoutStem
