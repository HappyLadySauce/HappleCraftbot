# 读取HappleCraft服务器状态数据
# 本模块用于读取远端服务器的JSON文件,并进行数据处理然后返回

import asyncio
import json
import aiohttp

# bs转GB
GB = 1024 ** 3

# 纯文本形式
async def server():
        data = await curl("http://game.happlelaoganma.cn:24567/v1/server")
        if data:
            try:
                tps = data.get('tps', 0)
                online_players = data.get('onlinePlayers', 0)
                total_memory = data['health']['totalMemory']
                maxmemory = data['health']['maxMemory']
                total_memory /= GB
                maxmemory /= GB
                total_memory = round(total_memory, 1)
                maxmemory = round(maxmemory, 1)
                return (f"收到指令\n"
                f"HappleCraft的服务器状态如下:\n"
                f"服务器TPS为: {tps}\n"
                f"服务器在线玩家数量: {online_players}\n"
                f"MC内存{total_memory}/{maxmemory}GB\n")
            except Exception as e:
                print(f"处理数据时出错: {e}")
                return "处理服务器状态数据时出错\n"
        else:
            return (f"收到指令\n"
                    f"但是服务器状态请求失败了QAQ\n"
                    f"请检查服务器运行状态\n")


async def curl(url):
    try:
        async with aiohttp.ClientSession() as session:
            # 设置超时时间为5秒
            timeout = aiohttp.ClientTimeout(total=5)
            async with session.get(url, timeout=timeout) as resp:
                # 确保响应状态码为200，表示请求成功
                if resp.status == 200:
                    content = await resp.text()
                    content_json_obj = json.loads(content)
                    return content_json_obj
                else:
                    print(f"请求失败，状态码: {resp.status}")
                    return None
    except aiohttp.ClientConnectionError as e:
        print(f"连接服务器失败: {e}")
        return None
    except asyncio.TimeoutError:
        print("请求超时")
        return None
    except json.JSONDecodeError:
        print("解析JSON失败")
        return None