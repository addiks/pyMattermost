
import httplib2
import json

from urllib.parse import urlparse

from .FileModel import FileModel
from .TeamModel import TeamModel
from .ServerLoggedInModel import ServerLoggedInModel

# https://api.mattermost.com/

class ServerModel:
    __http = None
    __url = None
    __urlParsed = None # urlparse.ParseResult
    __isReachable = None
    __loggedInModels = {}

    def __init__(self, url):
        while url[-1] == "/" and len(url) > 0:
            url = url[0:-1]
        self.__url = url
        self.__urlParsed = urlparse(url)
        self.__http = httplib2.Http()

    def getUrl(self):
        return self.__url

    def getUrlScheme(self):
        return self.__urlParsed.scheme

    def getUrlHostname(self):
        return self.__urlParsed.hostname

    def getUrlPort(self):
        return self.__urlParsed.port

    def getUrlPath(self):
        return self.__urlParsed.path

    def ping(self):
        url = self.__url + "/api/v3"

        isReachable = False

        try:
            responseHeaders, contentJson = self.__http.request(url, "GET")
            if type(contentJson) == bytes:
                contentJson = contentJson.decode()
            try:
                content = json.loads(contentJson)
                if type(content) == dict and 'id' in content and content['id'] == 'api.context.404.app_error':
                    isReachable = True
            except:
                pass
        except:
            pass

        self.__isReachable = isReachable

    def isReachable(self):
        if self.__isReachable == None:
            self.ping()
        return self.__isReachable

    def login(self, username, password):
        loggedInModel = None

        if username in self.__loggedInModels:
            loggedInModel = self.__loggedInModels[username]

        else:
            loggedInModel = ServerLoggedInModel(self, username, password)
            self.__loggedInModels[username] = loggedInModel

        return loggedInModel

    def callServer(self, method, route, data=None, headers={}, version="v3", returnPlainResponse=False):
        if not self.isReachable():
            raise Exception("Mattermost-Server %s is not reachable!" % self.__url)

        url = self.__url + "/api/" + version + route

        print(url)

        dataJson = None
        if data != None:
            dataJson = json.dumps(data)

        responseHeaders, contentJson = self.__http.request(
            url,
            method,
            body=dataJson,
            headers=headers
        )

        if returnPlainResponse:
            content = contentJson

        else:
            if type(contentJson) == bytes:
                contentJson = contentJson.decode()

            content = json.loads(contentJson)

        return responseHeaders, content
