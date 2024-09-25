import os
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message, GroupMessage
import setproctitle

from Module.about import craft
# 自定义模块
from Module.server import server


# 定义日志路径
log_dir = 'Log'
start_log_path = os.path.join('botpy.log')
group_log_path = os.path.join(log_dir, 'group')
channel_log_path = os.path.join(log_dir, 'channel')
# 定义日志记录
_log = logging.get_logger()
_log_group = logging.get_logger(group_log_path)
_log_channel = logging.get_logger(channel_log_path)
# 删除上一次bot运行日志
# if os.path.exists(start_log_path):
#     os.remove(start_log_path)


#======================================================================================================================#

# 机器人运行流程

class HappleCraftBot(botpy.Client):
    # 机器人准备好时触发
    async def on_ready(self):
        _log.info(f"{self.robot.name} 已经准备好了")

#----------------------------------------------------------------------------------------------------------------------#

    # 监听公域消息事件
    # 当收到@机器人的消息时
    # on_at_message_create(self, message: Message)
    # 当频道的消息被删除时
    # on_public_message_delete(self, message: Message)
    async def on_group_at_message_create(self, message: GroupMessage):
        # 封装回复函数,msg_type参数说明
        # 消息类型： 0 文本，2 是 markdown，3 ark 消息，4 embed，7 media 富媒体
        async def on_group_at_reply(response, msg_type):
            await message._api.post_group_message(
                group_openid=message.group_openid,
                msg_type=msg_type,
                msg_id=message.id,
                content=response
            )
            _log_group.info(f"\ngroup_openid: %s, \nmsg_id: %s, \n回复消息content: \"%s\"\n", message.group_openid, message.id, response)
        # 记录用户发送消息
        _log_group.info(f"\nMessage ID: %s, \n接受消息content: %s", message.id, message.content)

        # 开始执行公域事件
        if "/Server" in message.content:
            response = await server()
            # 返回用户消息
            await on_group_at_reply(response, 0)
        elif "/Craft" in message.content:
            response = await craft()
            # 返回用户消息
            await on_group_at_reply(response, 0)


# ----------------------------------------------------------------------------------------------------------------------#

    # 监听私域消息事件
    # 发送消息事件，代表频道内的全部消息，而不只是 at 机器人的消息。内容与 AT_MESSAGE_CREATE 相同
    # on_message_create(self, message: Message)
    # 删除（撤回）消息事件
    # on_message_delete(self, message: Message)
    async def on_message_create(self, message: Message):
        # 封装回复函数
        async def on_message_reply(response):
            await message._api.post_message(
                channel_id=message.channel_id,
                msg_id=message.id,
                content=response
            )
            _log_channel.info(f"\nchannle_id: %s, \nmsg_id: %s, \n回复消息content: \"%s\"\n", message.channel_id,message.id, response)

        # 记录用户发送消息
        _log_channel.info(f"\nMessage ID: %s, \n接受消息content: %s", message.id, message.content)

        # 开始执行私域事件
        if "/Server" in message.content:
            response = await server()
            # 返回用户消息
            await on_message_reply(response)
        elif "/Craft" in message.content:
            response = await craft()
            # 返回用户消息
            await on_message_reply(response)


# ----------------------------------------------------------------------------------------------------------------------#

    # 私信事件的监听
    # 当收到用户发给机器人的私信消息时
    # on_direct_message_create(self, message: DirectMessage)
    # 删除（撤回）消息事件
    # on_direct_message_delete(self, message: DirectMessage)

#----------------------------------------------------------------------------------------------------------------------#

    # 消息相关互动事件的监听
    # 为消息添加表情表态
    # on_message_reaction_add(self, reaction: Reaction)
    # 为消息删除表情表态
    # on_message_reaction_remove(self, reaction: Reaction)

#----------------------------------------------------------------------------------------------------------------------#

    # 频道事件监听
    # 当机器人加入新guild时
    # on_guild_create(self, guild: Guild)
    # 当guild资料发生变更时
    # on_guild_update(self, guild: Guild)
    # 当机器人退出guild时
    # on_guild_delete(self, guild: Guild)
    # 当channel被创建时
    # on_channel_create(self, channel: Channel)
    # 当channel被更新时
    # on_channel_update(self, channel: Channel)
    # 当channel被删除时
    # on_channel_delete(self, channel: Channel)

#----------------------------------------------------------------------------------------------------------------------#

    # 频道成员事件
    # 当成员加入时
    # on_guild_member_add(self, member: Member)
    # 当成员资料变更时
    # on_guild_member_update(self, member: Member)
    # 当成员被移除时
    # on_guild_member_remove(self, member: Member)

#----------------------------------------------------------------------------------------------------------------------#

    # 互动事件
    # 当收到用户发给机器人的私信消息时
    # on_interaction_create(self, interaction: Interaction)


#======================================================================================================================#
# 程序入口

# 读取appid和secret
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

if __name__ == "__main__":

    # 设置进程名
    setproctitle.setproctitle('mcbot')
    # 监听公域消息事件,监听私域消息事件,私信事件,消息互动相关事件,频道事件监听,频道成员事件,互动事件
    intents = botpy.Intents(public_messages=True, guild_messages=True, direct_message=True, guild_message_reactions=True, guilds=True, guild_members=True, interaction=True)
    # 创建机器人实例
    client = HappleCraftBot(intents=intents)
    # 运行机器人
    client.run(appid=test_config["appid"], secret=test_config["secret"])