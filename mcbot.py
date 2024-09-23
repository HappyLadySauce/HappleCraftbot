import os
import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message, GroupMessage
import requests
import setproctitle

#bs转GB
GB = 1024 * 1024 * 1024

#定义日志记录
_log = logging.get_logger()
_log_group = logging.get_logger("group")
_log_at = logging.get_logger("at")

#读取appid和secret
test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

#机器人运行流程
class HappleCraftBot(botpy.Client):
    #机器人准备好时触发
    async def on_ready(self):
        print(f"{self.robot.name} 已经准备好了")
        _log.info(f"{self.robot.name} 已经准备好了")


    #监听公域消息事件
    #当收到@机器人的消息时
    #on_at_message_create(self, message: Message)
    #当频道的消息被删除时
    #on_public_message_delete(self, message: Message)
    async def on_group_at_message_create(self, message: GroupMessage):
        if "/server" in message.content:
            data = await curl("http://game.happlelaoganma.cn:4567/v1/server")
            if data:
                try:
                    tps = data.get('tps', 0)
                    online_players = data.get('onlinePlayers', 0)
                    total_memory = data['health']['totalMemory']
                    maxmemory = data['health']['maxMemory']
                    freememory = data['health']['freeMemory']
                    total_memory /= GB
                    maxmemory /= GB
                    freememory /= GB
                    total_memory = round(total_memory, 1)
                    maxmemory = round(maxmemory, 1)
                    freememory = round(freememory, 1)
                    messageResult = await message._api.post_group_message(
                        group_openid=message.group_openid,
                        msg_type=0,
                        msg_id=message.id,
                        content=f"{self.robot.name}收到指令\n "
                                f"HappleCraft的服务器状态如下:\n"
                                f"服务器TPS为: {tps}\n"
                                f"服务器在线玩家数量: {online_players}\n"
                                f"MC内存{total_memory}/{maxmemory}G\n"
                                f"服务器剩余内存{freememory}G\n"
                                f"服务器总内存为MC内存+服务器剩余内存+已使用内存")
                    _log.info(messageResult)
                except Exception as e:
                    print(f"处理数据时出错: {e}")
                    await message.reply(content="处理服务器状态数据时出错")
            else:
                await message.reply(content=f"{self.robot.name}收到指令，但server状态请求失败")


    #监听私域消息事件
    #发送消息事件，代表频道内的全部消息，而不只是 at 机器人的消息。内容与 AT_MESSAGE_CREATE 相同
    #on_message_create(self, message: Message)
    #删除（撤回）消息事件
    #on_message_delete(self, message: Message)
    async def on_message_create(self, message: Message):
        _log.info(message.author.avatar)
        if "/server" in message.content:
            await message.reply(content=f"Test Success!\n")


    #私信事件的监听
    #当收到用户发给机器人的私信消息时
    #on_direct_message_create(self, message: DirectMessage)
    #删除（撤回）消息事件
    #on_direct_message_delete(self, message: DirectMessage)


    #消息相关互动事件的监听
    #为消息添加表情表态
    #on_message_reaction_add(self, reaction: Reaction)
    #为消息删除表情表态
    #on_message_reaction_remove(self, reaction: Reaction)


    #频道事件监听
    #当机器人加入新guild时
    #on_guild_create(self, guild: Guild)
    #当guild资料发生变更时
    #on_guild_update(self, guild: Guild)
    #当机器人退出guild时
    #on_guild_delete(self, guild: Guild)
    #当channel被创建时
    #on_channel_create(self, channel: Channel)
    #当channel被更新时
    #on_channel_update(self, channel: Channel)
    #当channel被删除时
    #on_channel_delete(self, channel: Channel)


    #频道成员事件
    #当成员加入时
    #on_guild_member_add(self, member: Member)
    #当成员资料变更时
    #on_guild_member_update(self, member: Member)
    #当成员被移除时
    #on_guild_member_remove(self, member: Member)


    #互动事件
    #当收到用户发给机器人的私信消息时
    #on_interaction_create(self, interaction: Interaction)


async def curl(url):
    try:
        # 发送GET请求
        responses = requests.get(url)
        if responses.status_code != 200:
            print(f"请求失败，状态码: {responses.status_code}")
        else:
            # 成功返回json文件内容
            return responses.json()
    except requests.exceptions.RequestException as e:
        # 捕获并打印异常信息
        print(f"请求出错:{e}")
        return None


#程序入口
if __name__ == "__main__":

    #设置进程名
    setproctitle.setproctitle('mcbot')
    #监听公域消息事件,监听私域消息事件,私信事件,消息互动相关事件,频道事件监听,频道成员事件,互动事件
    intents = botpy.Intents(public_messages=True, guild_messages=True, direct_message=True, guild_message_reactions=True, guilds=True, guild_members=True, interaction=True)
    #创建机器人实例
    client = HappleCraftBot(intents=intents)
    #运行机器人
    client.run(appid=test_config["appid"], secret=test_config["secret"])