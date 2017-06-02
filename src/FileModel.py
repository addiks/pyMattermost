

class FileModel:
    __fileId = None
    __fileContents = None
    __serverModel = None  # Mattermost.ServerLoggedInModel

    def __init__(self, serverModel, fileId, fileContents):
        self.__serverModel = serverModel
        self.__fileId = fileId
        self.__fileContents = fileContents

    def getId(self):
        return self.__fileId

    def getFileContents(self):
        return self.__fileContents

    def getFileThumbnail(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/get_thumbnail")

    def getFilePreview(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/get_preview")

    def getFileInfo(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/get_info")

    def getFilePublicLink(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/get_public_link")

    def callServer(self, method, route, data=None):
        return self.__serverModel.callServer(method, "/files/%s%s" % (self.__fileId, route), data)
