
import asyncio
import websockets
import json
import uuid

from gi.repository import GLib
from _thread import start_new_thread

from .TeamModel import TeamModel
from .UserModel import UserModel
from .FileModel import FileModel

class ServerLoggedInModel:
    __serverModel = None      # ServerModel
    __selfUser = None         # UserModel
    __webSocket = None        # websocket
    __webSocketSeq = 0        # integer
    __webSocketCallbacks = {} # callback[]
    __eventListener = {}      # callback[]
    __userCache = {}
    __username = None
    __password = None
    __token = None
    __isStopping = False      # boolean

    def __init__(self, serverModel, username, password):
        if not serverModel.isReachable():
            raise Exception("Mattermost-Server %s is not reachable!" % serverModel.getUrl())

        responseHeaders, content = serverModel.callServer("POST", "/users/login", {
            'login_id': username,
            'password': password
        })

        if "token" not in responseHeaders:
            if "message" in content:
                raise Exception("Server response: %s" % content['message'])
            else:
                raise Exception("Cannot login on this server!")

        self.__serverModel = serverModel
        self.__token = responseHeaders['token']
        self.__username = username
        self.__password = password

        asyncio.get_event_loop().run_until_complete(self.__connectWebsocket())

        self.sendWebsocketRequest("authentication_challenge", {
            'token': self.__token
        })

        start_new_thread(asyncio.get_event_loop().run_until_complete, (self.__handleWebsocket(), ))

    async def __connectWebsocket(self):
        # ServerModel
        server = self.__serverModel

        scheme = server.getUrlScheme()
        hostname = server.getUrlHostname()
        port = server.getUrlPort()
        path = server.getUrlPath()

        webSocketScheme = 'ws'
        if scheme == "https":
            webSocketScheme = 'wss'

        portStr = ""
        if port != None:
            portStr = ":" + str(port)

        url = webSocketScheme + '://' + hostname + portStr + path + "/api/v3/users/websocket"

        print(url)

        webSocket = await websockets.connect(url)
        self.__webSocket = webSocket

    async def __handleWebsocket(self):
        # websockets.client.WebSocketClientProtocol
        webSocket = self.__webSocket

        while not self.__isStopping:
            try:
                messageJson = await webSocket.recv()

                print("per WS received: " + messageJson)

                message = json.loads(messageJson)

                if "seq_reply" in message:
                    seqNo = str(message["seq_reply"])
                    if seqNo in self.__webSocketCallbacks:
                        errorObject = None
                        if "error" in message:
                            errorObject = message["error"]
                        GLib.idle_add(self.__webSocketCallbacks[seqNo], message['status'], errorObject)

                if "event" in message:
                    eventName = str(message["event"])
                    eventData = message["data"]

                    if eventName in self.__eventListener:
                        broadcast = message["broadcast"]
                        for broadcastFilter, callback in self.__eventListener[eventName]:
                            if broadcastFilter == None:
                                GLib.idle_add(callback, eventData)
                            else:
                                matches = True
                                for broadcastKey in broadcastFilter:
                                    broadcastValue = broadcastFilter[broadcastKey]
                                    if broadcastValue != broadcast[broadcastKey]:
                                        matches = False
                                        break
                                if matches:
                                    GLib.idle_add(callback, eventData)

            except websockets.exceptions.ConnectionClosed as exception:
                # TODO: automatic reconnect after X seconds or minutes and notification to user
                raise exception

        webSocket.close()

    def registerTypingListener(self, callback, broadcast=None):
        self.registerEventListener("typing", callback, broadcast)

    def registerPostedListener(self, callback, broadcast=None):
        self.registerEventListener("posted", callback, broadcast)

    def registerPostEditedListener(self, callback, broadcast=None):
        self.registerEventListener("post_edited", callback, broadcast)

    def registerPostDeletedListener(self, callback, broadcast=None):
        self.registerEventListener("post_deleted", callback, broadcast)

    def registerNewUserListener(self, callback, broadcast=None):
        self.registerEventListener("new_user", callback, broadcast)

    def registerLeaveTeamListener(self, callback, broadcast=None):
        self.registerEventListener("leave_team", callback, broadcast)

    def registerUserAddedListener(self, callback, broadcast=None):
        self.registerEventListener("user_added", callback, broadcast)

    def registerUserUpdatedListener(self, callback, broadcast=None):
        self.registerEventListener("user_updated", callback, broadcast)

    def registerUserRemovedListener(self, callback, broadcast=None):
        self.registerEventListener("user_removed", callback, broadcast)

    def registerPreferenceChangedListener(self, callback, broadcast=None):
        self.registerEventListener("preference_changed", callback, broadcast)

    def registerEphemeralMessageListener(self, callback, broadcast=None):
        self.registerEventListener("ephemeral_message", callback, broadcast)

    def registerStatusChangeListener(self, callback, broadcast=None):
        self.registerEventListener("status_change", callback, broadcast)

    def registerHelloListener(self, callback, broadcast=None):
        self.registerEventListener("hello", callback, broadcast)

    def registerWebRTCListener(self, callback, broadcast=None):
        self.registerEventListener("webrtc", callback, broadcast)

    def requestStatuses(self, callback):
        self.sendWebsocketRequest("get_statuses", responseCallback=callback)

    def requestStatusesById(self, idList, callServer):
        self.sendWebsocketRequest("get_statuses_by_ids", idList, callback)
        # TODO: confirm that this is correct

    def registerEventListener(self, eventName, callback, broadcast=None):
        eventName = str(eventName)
        if eventName not in self.__eventListener:
            self.__eventListener[eventName] = []
        self.__eventListener[eventName].append([broadcast, callback])

    def sendWebsocketRequest(self, actionName, payloadData={}, responseCallback=None):
        self.__webSocketSeq += 1

        seqNo = str(self.__webSocketSeq)

        if responseCallback != None:
            self.__webSocketCallbacks[seqNo] = responseCallback

        data = {
            'seq': self.__webSocketSeq,
            'action': str(actionName),
            'data': payloadData
        }

        dataJson = json.dumps(data)

        result = self.__webSocket.send(dataJson)

        print(result)

        asyncio.get_event_loop().run_until_complete(result)

        print("per WS sent: " + dataJson)

    def logout(self):
        self.__isStopping = True
        # TODO send logout REST request

    def createUser(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/create")

    def getSelfUser(self):
        if self.__selfUser == None:
            headers, result = self.callServer("GET", "/users/me")
            self.__selfUser = UserModel.fromJsonUserObject(result, self)
        return self.__selfUser

    def logout(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/logout")

    def getUsers(self, limit=30):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/users/{offset}/%d" % limit)

    def searchUsers(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/search")

    def getUsersByIds(self, userIds):
        users = []
        print(userIds)
        userIdsToFetch = []
        for userId in userIds:
            if userId in self.__userCache:
                users.append(self.__userCache[userId])
            else:
                userIdsToFetch.append(userId)

        if len(userIdsToFetch) > 0:
            headers, result = self.callServer("POST", "/users/ids", userIdsToFetch)

            for userId in result:
                userJsonData = result[userId]
                user = UserModel.fromJsonUserObject(userJsonData, self)
                users.append(user)
                self.__userCache[userId] = user

        return users

    def getUserById(self, userId):
        user = None
        users = self.getUsersByIds([userId])
        if len(users) > 0:
            user = users[0]
        return user

    def updateUser(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/update")

    def updateUserRoles(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/update_roles")

    def updateUserIsActive(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/update_active")

    def updateUserNotificationProperties(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/update_notify")

    def updateUserPassword(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/newpassword")

    def sendPasswordResetMail(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/users/send_password_reset")

    def getUserImage(self, userId, lastPictureUpdate):
        imageData = None
        if lastPictureUpdate != None:
            url = "/users/%s/image?time=%d" % (userId, lastPictureUpdate)
            headers, imageData = self.callServer("GET", url, returnPlainResponse=True)
        return imageData

    def getFile(self, fileId):
        headers, fileContents = self.callServer("GET", "/files/%s/get" % fileId, returnPlainResponse=True)

        return FileModel(self, fileId, fileContents)

    def savePreferences(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/preferences/save")

    def deletePreferences(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/preferences/delete")

    def getPreferences(self, category):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/preferences/%s")

    def getPreference(self, category, name):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("GET", "/preferences/%s/%s" % (category, name))

    def createTeam(self):
        raise Exception("*UNIMPLEMENTED*")
        headers, result = self.callServer("POST", "/teams/create")

        return TeamModel(self, teamName) # TODO

    def getAllTeams(self):
        headers, teams = self.callServer("GET", "/teams/all")
        teamModels = []
        for teamId in teams:
            teamData = teams[teamId]
            teamModel = TeamModel.fromJsonTeamObject(self, teamData)
            teamModels.append(teamModel)
        return teamModels

    def teamExists(self, teamName):
        foundTeam = False
        teams = self.getAllTeams()
        for teamCandidate in teams:
            if teamCandidate.getName() == teamName:
                foundTeam = True
                break
        return foundTeam

    def getTeam(self, teamName):
        team = None
        teams = self.getAllTeams()
        for teamCandidate in teams:
            if teamCandidate.getName() == teamName:
                team = teamCandidate
                break
        if team == None:
            raise Exception("Team %s does not exist or is not accessable for this user!" % teamName)
        return team

    def createId(self):
        return str(uuid.uuid4())

    def callServer(self, method, route, data=None, headers={}, version="v3", returnPlainResponse=False):
        print("Token: " + str(self.__token))
        headers['Authorization'] = "Bearer " + self.__token
        return self.__serverModel.callServer(method, route, data, headers, version, returnPlainResponse)
