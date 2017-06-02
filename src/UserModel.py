
class UserModel:
    __serverModel = None        # ServerLoggedInModel
    __userId = None             # string
    __createAt = None           # integer
    __updateAt = None           # integer
    __deleteAt = None           # integer
    __username = None           # string
    __firstName = None          # string
    __lastName = None           # string
    __nickname = None           # string
    __email = None              # string
    __emailVerified = None      # boolean
    __password = None           # string
    __authData = None           # string
    __authService = None        # string
    __roles = None              # string
    __locale = None             # string
    __notifyProps = None        # object
    __props = None              # object
    __lastPasswordUpdate = None # integer
    __lastPictureUpdate = None  # integer
    __failedAttempts = None     # integer
    __mfaActive = None          # boolean
    __mfaSecret = None          # string

    @staticmethod
    def fromJsonUserObject(data, serverModel):
        for key in [
            "password",
            "props",
            "failed_attempts",
            "mfa_active",
            "mfa_secret",
            "email_verified",
            "notify_props",
            "last_password_update",
            "last_picture_update"
        ]:
            if key not in data:
                data[key] = None
        return UserModel(
            serverModel,
            data['id'],
            data['create_at'],
            data['update_at'],
            data['delete_at'],
            data['username'],
            data['first_name'],
            data['last_name'],
            data['nickname'],
            data['email'],
            data['email_verified'],
            data['password'],
            data['auth_data'],
            data['auth_service'],
            data['roles'],
            data['locale'],
            data['notify_props'],
            data['props'],
            data['last_password_update'],
            data['last_picture_update'],
            data['failed_attempts'],
            data['mfa_active'],
            data['mfa_secret'],
        )

    def __init__(
        self,
        serverModel,
        userId,
        createAt,
        updateAt,
        deleteAt,
        username,
        firstName,
        lastName,
        nickname,
        email,
        emailVerified,
        password,
        authData,
        authService,
        roles,
        locale,
        notifyProps,
        props,
        lastPasswordUpdate,
        lastPictureUpdate,
        failedAttempts,
        mfaActive,
        mfaSecret,
    ):
        self.__serverModel = serverModel
        self.__userId = userId
        self.__createAt = createAt
        self.__updateAt = updateAt
        self.__deleteAt = deleteAt
        self.__username = username
        self.__firstName = firstName
        self.__lastName = lastName
        self.__nickname = nickname
        self.__email = email
        self.__emailVerified = emailVerified
        self.__password = password
        self.__authData = authData
        self.__authService = authService
        self.__roles = roles
        self.__locale = locale
        self.__notifyProps = notifyProps
        self.__props = props
        self.__lastPasswordUpdate = lastPasswordUpdate
        self.__lastPictureUpdate = lastPictureUpdate
        self.__failedAttempts = failedAttempts
        self.__mfaActive = mfaActive
        self.__mfaSecret = mfaSecret

    def getId(self):
        return self.__userId

    def getFullName(self):
        return self.__firstName + " " + self.__lastName

    def getLastPictureUpdate(self):
        return self.__lastPictureUpdate

    def getImage(self):
        # ServerLoggedInModel
        serverModel = self.__serverModel

        return serverModel.getUserImage(self.__userId, self.__lastPictureUpdate)

    def getUseName(self):
        usename = "[unknown]"

        firstname = self.__firstName
        lastname = self.__lastName
        username = self.__username

        if len(firstname) > 0 and len(lastname) > 0:
            usename = self.getFullName()

        elif len(firstname) > 0:
            usename = firstname

        elif len(lastname) > 0:
            usename = lastname

        elif len(username) > 0:
            usename = username

        return usename
