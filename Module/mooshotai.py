import asyncio
import os

import aiohttp
import requests
import yaml
from openai import OpenAI

#=====================================================================================================================#

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
apikey = test_config.get("mooshotai_apikey", None)

client = OpenAI(
    api_key = apikey,
    base_url = "https://api.moonshot.cn/v1",
)

#=====================================================================================================================#

# rmb余额查询API
balance_headers = {
    'Authorization': f'Bearer {apikey}'
}
balance_url = 'https://api.moonshot.cn/v1/users/me/balance'

async def fetch_balance(session):
    try:
        # 发送 GET 请求
        async with session.get(balance_url, headers=balance_headers) as response:
            # 检查响应状态码
            if response.status == 200:
                # 将响应内容解析为 JSON
                data = await response.json()
                # print('Available Balance:', data['data']['available_balance'])
                # print('Voucher Balance:', data['data']['voucher_balance'])
                # print('Cash Balance:', data['data']['cash_balance'])
                return data
            else:
                print('Failed to retrieve data:', response.status)
    except aiohttp.ClientError as e:
        # 打印异常信息
        print(e)

#=====================================================================================================================#

# tokens查询API
tokens = 0
def use_token(tokens):
    return f"{tokens * 0.000012:.6f}"

# 构建请求头部
token_headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {apikey}'
}

# API 的 URL
token_url = 'https://api.moonshot.cn/v1/tokenizers/estimate-token-count'

def fetch_token(data):
    try:
        # 发送 POST 请求
        response = requests.post(token_url, headers=token_headers, json=data)
        # 检查响应状态码
        if response.status_code == 200:
            response_data = response.json()
            return response_data['data']['total_tokens']
        else:
            print('Failed to retrieve data:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        # 打印异常信息
        print(e)
        return None

#=====================================================================================================================#

# tools = [
#     {
#         "type": "function",  # 约定的字段 type，目前支持 function 作为值
#         "function": {  # 当 type 为 function 时，使用 function 字段定义具体的函数内容
#             "name": "search",  # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
#             "description": """
# 				通过搜索引擎搜索互联网上的内容。
#
# 				当你的知识无法回答用户提出的问题，或用户请求你进行联网搜索时，调用此工具。请从与用户的对话中提取用户想要搜索的内容作为 query 参数的值。
# 				搜索结果包含网站的标题、网站的地址（URL）以及网站简介。
# 			""",  # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
#             "parameters": {  # 使用 parameters 字段来定义函数接收的参数
#                 "type": "object",  # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
#                 "required": ["query"],  # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
#                 "properties": {  # properties 中是具体的参数定义，你可以定义多个参数
#                     "query": {  # 在这里，key 是参数名称，value 是参数的具体定义
#                         "type": "string",  # 使用 type 定义参数类型
#                         "description": """
# 							用户搜索的内容，请从用户的提问或聊天上下文中提取。
# 						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
#                     }
#                 }
#             }
#         }
#     },
#     {
#     	"type": "function", # 约定的字段 type，目前支持 function 作为值
#     	"function": { # 当 type 为 function 时，使用 function 字段定义具体的函数内容
#     		"name": "crawl", # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
#     		"description": """
#     			根据网站地址（URL）获取网页内容。
#     		""", # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
#     		"parameters": { # 使用 parameters 字段来定义函数接收的参数
#     			"type": "object", # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
#     			"required": ["url"], # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
#     			"properties": { # properties 中是具体的参数定义，你可以定义多个参数
#     				"url": { # 在这里，key 是参数名称，value 是参数的具体定义
#     					"type": "string", # 使用 type 定义参数类型
#     					"description": """
#     						需要获取内容的网站地址（URL），通常情况下从搜索结果中可以获取网站的地址。
#     					""" # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
#     				}
#     			}
#     		}
#     	}
#     }
# ]
#
# def search_impl(query: str) -> List[Dict[str, Any]]:
#     """
#     search_impl 使用搜索引擎对 query 进行搜索，目前主流的搜索引擎（例如 Bing）都提供了 API 调用方式，你可以自行选择
#     你喜欢的搜索引擎 API 进行调用，并将返回结果中的网站标题、网站链接、网站简介信息放置在一个 dict 中返回。
#
#     这里只是一个简单的示例，你可能需要编写一些鉴权、校验、解析的代码。
#     """
#     r = httpx.get("https://your.search.api", params={"query": query})
#     return r.json()
#
#
# def search(arguments: Dict[str, Any]) -> Any:
#     query = arguments["query"]
#     result = search_impl(query)
#     return {"result": result}
#
#
# def crawl_impl(url: str) -> str:
#     """
#     crawl_url 根据 url 获取网页上的内容。
#
#     这里只是一个简单的示例，在实际的网页抓取过程中，你可能需要编写更多的代码来适配复杂的情况，例如异步加载的数据等；同时，在获取
#     网页内容后，你可以根据自己的需要对网页内容进行清洗，只保留文本或移除不必要的内容（例如广告信息等）。
#     """
#     r = httpx.get(url)
#     return r.text
#
#
# def crawl(arguments: dict) -> str:
#     url = arguments["url"]
#     content = crawl_impl(url)
#     return {"content": content}
#
#
# # 通过 tool_map 将每个工具名称及其对应的函数进行映射，以便在 Kimi 大模型返回 tool_calls 时能快速找到应该执行的函数
# tool_map = {
#     "search": search,
#     "crawl": crawl,
# }

#=====================================================================================================================#

# 我们将 System Messages 单独放置在一个列表中，这是因为每次请求都应该携带 System Messages
system_messages = [
    {"role": "system",
     "content": "你是 HappleCraftBot，服务于 HappleCraft 交流群，HappleCraft 是一个我的世界服务器的名称，它同时提供多个我的世界服务端，为玩家们提供良好的，新奇的游戏体验。并且还有一个交流群，你 HappleCraftBot 也在群里，你的发言会让群里的网友看见。注意你的言论不要违反QQ群的发言规则，你服务于群聊尽力为用户(网友)提供友善良好的服务。你还有两个功能: 向你发送 /Server 能提供查看我的世界服务器状态的功能，还有向你发送 /Craft 可以查看服主的简介和个人博客。"}
    # {"role": "user", "content": "请联网搜索 Context Caching，并告诉我它是什么。"}  # 在提问中要求 Kimi 大模型联网搜索
]

# 我们定义一个全局变量 messages，用于记录我们和 Kimi 大模型产生的历史对话消息
# 在 messages 中，既包含我们向 Kimi 大模型提出的问题（role=user），也包括 Kimi 大模型给我们的回复（role=assistant）
# messages 中的消息按时间顺序从小到大排列
messages = []

def make_messages(input: str, n: int = 2) -> list[dict]:
    """
    使用 make_messages 控制每次请求的消息数量，使其保持在一个合理的范围内，例如默认值是 20。在构建消息列表
    的过程中，我们会先添加 System Prompt，这是因为无论如何对消息进行截断，System Prompt 都是必不可少
    的内容，再获取 messages —— 即历史记录中，最新的 n 条消息作为请求使用的消息，在大部分场景中，这样
    能保证请求的消息所占用的 Tokens 数量不超过模型上下文窗口。
    """
    # 首先，我们将用户最新的问题构造成一个 message（role=user），并添加到 messages 的尾部
    global messages
    messages.append({
        "role": "user",
        "content": input,
    })
    # new_messages 是我们下一次请求使用的消息列表，现在让我们来构建它
    new_messages = []
    # 每次请求都需要携带 System Messages，因此我们需要先把 system_messages 添加到消息列表中；
    # 注意，即使对消息进行截断，也应该注意保证 System Messages 仍然在 messages 列表中。
    new_messages.extend(system_messages)
    # 在这里，当历史消息超过 n 条时，我们仅保留最新的 n 条消息
    if len(messages) > n:
        messages = messages[-n:]
    new_messages.extend(messages)
    return new_messages

#=====================================================================================================================#

def chat(input: str) -> str:
    new_messages = make_messages(input)
    # 携带 messages 与 Kimi 大模型对话
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=new_messages,
        temperature=0.3,
        # tools=tools,
    )

    # 查询使用token
    data = {
        "model": "moonshot-v1-8k",
        "messages": new_messages
    }
    global tokens
    tokens = fetch_token(data)

    # 通过 API 我们获得了 Kimi 大模型给予我们的回复消息（role=assistant）
    assistant_message = completion.choices[0].message
    messages.append(assistant_message)
    return assistant_message.content

#=====================================================================================================================#

async def kimi(content):
    async with aiohttp.ClientSession() as session:
        data = await fetch_balance(session)
        balance = data['data']['available_balance']
    sem = asyncio.Semaphore(10)
    async with sem:
        # 使用 asyncio.to_thread 在线程池中运行同步函数
        response = await asyncio.to_thread(chat, content)
        response = f"{response}\n本次消耗token: {tokens}\n消耗rmb: {use_token(tokens)}\n机器人余额: {balance}rmb"
        return response









