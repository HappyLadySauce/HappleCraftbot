#读取HappleCraft服务器状态数据
#本模块用于读取远端服务器的JSON文件,并进行数据处理然后返回

import aiohttp

#bs转GB
GB = 1024 * 1024 * 1024

async def server(content):
    if "/server" in content:
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
                return (f"收到指令\n"
                f"HappleCraft的服务器状态如下:\n"
                f"服务器TPS为: {tps}\n"
                f"服务器在线玩家数量: {online_players}\n"
                f"MC内存{total_memory}/{maxmemory}GB\n"
                f"服务器剩余内存{freememory}GB\n"
                f"服务器总内存为MC内存+服务器剩余内存+已使用内存")
            except Exception as e:
                print(f"处理数据时出错: {e}")
                return "处理服务器状态数据时出错\n"
        else:
            return (f"收到指令\n"
                    f"但是服务器状态请求失败了QAQ\n"
                    f"请检查服务器运行状态\n")


async def curl(url):
    try:
        # 发送GET请求
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"请求失败，状态码: {response.status}")
                    return None
                else:
                    # 成功返回json文件内容
                    return await response.json()
    except aiohttp.ClientConnectionError as e:
        print(f"连接服务器失败: {e}")
        return None