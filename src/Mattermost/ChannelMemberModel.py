
class ChannelMemberModel:
    __teamModel = None # TeamModel
    __channelId = None # int
    __userId = None # int
    __roles = None # string
    __lastUpdatedAt = None # int
    __lastViewedAt = None # int
    __mentionCount = None # int
    __messageCount = None # int
    __notifyProps = None # object

    @staticmethod
    def fromJsonChannelMemberObject(teamModel, data):
        print(data)

        return ChannelMemberModel(
            teamModel,
            data['channel_id'],
            data['user_id'],
            data['roles'],
            data['last_update_at'],
            data['last_viewed_at'],
            data['mention_count'],
            data['msg_count'],
            data['notify_props']
        )

    def __init__(
        self,
        teamModel,
        channelId,
        userId,
        roles,
        lastUpdatedAt,
        lastViewedAt,
        mentionCount,
        messageCount,
        notifyProps
    ):
        self.__teamModel = teamModel
        self.__channelId = channelId
        self.__userId = userId
        self.__roles = roles
        self.__lastViewedAt = lastViewedAt
        self.__mentionCount = mentionCount
        self.__messageCount = messageCount
        self.__notifyProps = notifyProps

    def getUser(self):
        return self.__teamModel.getServer().getUserById(self.__userId)

    def getChannel(self):
        return self.__teamModel.getChannel(self.__channelId)
