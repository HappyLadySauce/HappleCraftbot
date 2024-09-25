import os
from multiprocessing.sharedctypes import synchronized

import aiohttp
import yaml

# 读取apikey
def read(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# 获取当前文件的目录
current_directory = os.path.dirname(__file__)
# 构建配置文件的路径
config_path = os.path.join(current_directory, "config.yaml")
# 读取配置文件
test_config = read(config_path)
# 获取 apikey
apikey = test_config.get("apikey", None)

# 获取远程节点列表
server_url = f'http://game.happlelaoganma.cn:20000/api/service/remote_services_system?apikey={apikey}'
# auth_url = f'http://game.happlelaoganma.cn:20000/api/auth/search?apikey={apikey}&userName=ssddffaa&page=1&page_size=20&role=10'
instance_url = f'http://game.happlelaoganma.cn:20000/api/instance?apikey={apikey}'
headers = {
    'Content-Type': 'application/json; charset=utf-8',
    'X-Requested-With': 'XMLHttpRequest'
}

#--------------------------------------------------------------------------------------------------------------------#

auth_url = f'http://game.happlelaoganma.cn:20000/api/auth/search?apikey={apikey}&userName=ssddffaa&page=1&page_size=20&role=10'

def instance_json_to_dict(json_data):
    users_data = json_data.get('data', {}).get('data', [])
    instances_list = []
    for user in users_data:
        for instance in user.get('instances', []):
            instance_info = {
                'uuid': instance.get('instanceUuid'),
                'daemonId': instance.get('daemonId')
            }
            instances_list.append(instance_info)
    return instances_list

async def auth():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(auth_url, headers=headers) as response:
                if response.status == 200:
                    response_json = await response.json()
                    if not response_json.get('data', {}).get('data', []):
                        print("No instances found.")
                        return []
                    return instance_json_to_dict(response_json)
                else:
                    print(f"Failed to retrieve data: Status code {response.status}")
                    error_text = await response.text()
                    print("Error details:", error_text)
                    return None
        except aiohttp.ClientError as e:
            print(f"An HTTP client error occurred: {e}")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


def instance_json_to_text(json_data, node_number):
    data = json_data['data']
    instance_info = f"UUID: {data['instanceUuid']}\n启动次数: {data['started']}, 状态: {data['status']}"
    system_info = f"当前玩家: {data['info']['currentPlayers']}"
    cpu_usage_percent = f"{data['processInfo']['cpu']:.1%}"
    memory_usage_gb = round(data['processInfo']['memory'] / (1024 ** 3), 1)
    elapsed_time_hours = round(data['processInfo']['elapsed'] / 36000, 1)
    process_info = f"CPU使用率: {cpu_usage_percent}, 内存使用: {memory_usage_gb}GB\n创建时间: {data['processInfo']['ctime']}, 运行时间: {elapsed_time_hours}小时"
    text = f"节点编号: Node{node_number}:\n实例信息:\n{instance_info}\n{system_info}\n{process_info}"
    return text

async def instances():
    instance_params_list = await auth()
    if instance_params_list:
        results = []
        async with aiohttp.ClientSession() as session:
            for instance_params in instance_params_list:
                try:
                    async with session.get(instance_url, headers=headers, params=instance_params) as response:
                        if response.status == 200:
                            response_json = await response.json()
                            result = instance_json_to_text(response_json, list(instance_params.keys()).index('uuid') + 1)
                            results.append(result)
                        else:
                            print(f"Failed to retrieve data for instance: Status code {response.status}")
                            error_text = await response.text()
                            print("Error details:", error_text)
                except aiohttp.ClientError as e:
                    print(f"An HTTP client error occurred: {e}")
                except Exception as e:
                    print(f"An error occurred: {e}")
        return results
    else:
        print("Failed to get instance parameters from auth function")
        return []

async def instance():
    instances_list = await instances()
    instance_text = ""
    for index, instance_data in enumerate(instances_list, start=1):
        instance_text += f"收到请求:\n{instance_data}\n\n"
    return instance_text.strip()


#--------------------------------------------------------------------------------------------------------------------#

def server_json_to_text(json_data):
    content = []
    for index, node in enumerate(json_data['data'], start=1):
        content.append(f"收到请求:")
        content.append(f"节点编号: Node{index}")
        content.append(f"运行中的实例: {node['instance']['running']}, 总实例数: {node['instance']['total']}")
        cpu_usage_percent = f"{node['system']['cpuUsage']:.1%}"
        mem_usage_percent = f"{node['system']['memUsage']:.1%}"
        content.append(f"CPU使用率: {cpu_usage_percent}, 内存使用率: {mem_usage_percent}")
        # 将内存转换为 GB 并保留一位小数
        total_mem_gb = round(node['system']['totalmem'] / (1024 ** 3), 1)
        free_mem_gb = round(node['system']['freemem'] / (1024 ** 3), 1)
        content.append(f"总内存: {total_mem_gb}GB, 空闲内存: {free_mem_gb}GB")
        # 添加空行以分隔不同的节点数据
        content.append("")
    return "\n".join(content)

async def node():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(server_url, headers=headers) as response:
                if response.status == 200:
                    return server_json_to_text(await response.json())
                else:
                    # 请求失败，打印错误信息
                    print(f"Failed to retrieve data: Status code {response.status}")
                    error_text = await response.text()
                    print("Error details:", error_text)
        except aiohttp.ClientError as e:
            print(f"An HTTP client error occurred: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

#--------------------------------------------------------------------------------------------------------------------#







