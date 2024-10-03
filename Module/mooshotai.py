import os
import yaml
from openai import OpenAI

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

# 我们将 System Messages 单独放置在一个列表中，这是因为每次请求都应该携带 System Messages
system_messages = [
    {"role": "system",
     "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。"},
]

# 我们定义一个全局变量 messages，用于记录我们和 Kimi 大模型产生的历史对话消息
# 在 messages 中，既包含我们向 Kimi 大模型提出的问题（role=user），也包括 Kimi 大模型给我们的回复（role=assistant）
# messages 中的消息按时间顺序从小到大排列
messages = []


def make_messages(input: str, n: int = 20) -> list[dict]:
    """
    使用 make_messaegs 控制每次请求的消息数量，使其保持在一个合理的范围内，例如默认值是 20。在构建消息列表
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


tools = [
    {
        "type": "function",  # 约定的字段 type，目前支持 function 作为值
        "function": {  # 当 type 为 function 时，使用 function 字段定义具体的函数内容
            "name": "search",  # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
            "description": """ 
				通过搜索引擎搜索互联网上的内容。

				当你的知识无法回答用户提出的问题，或用户请求你进行联网搜索时，调用此工具。请从与用户的对话中提取用户想要搜索的内容作为 query 参数的值。
				搜索结果包含网站的标题、网站的地址（URL）以及网站简介。
			""",  # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
            "parameters": {  # 使用 parameters 字段来定义函数接收的参数
                "type": "object",  # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
                "required": ["query"],  # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
                "properties": {  # properties 中是具体的参数定义，你可以定义多个参数
                    "query": {  # 在这里，key 是参数名称，value 是参数的具体定义
                        "type": "string",  # 使用 type 定义参数类型
                        "description": """
							用户搜索的内容，请从用户的提问或聊天上下文中提取。
						"""  # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
                    }
                }
            }
        }
    },
    # {
    # 	"type": "function", # 约定的字段 type，目前支持 function 作为值
    # 	"function": { # 当 type 为 function 时，使用 function 字段定义具体的函数内容
    # 		"name": "crawl", # 函数的名称，请使用英文大小写字母、数据加上减号和下划线作为函数名称
    # 		"description": """
    # 			根据网站地址（URL）获取网页内容。
    # 		""", # 函数的介绍，在这里写上函数的具体作用以及使用场景，以便 Kimi 大模型能正确地选择使用哪些函数
    # 		"parameters": { # 使用 parameters 字段来定义函数接收的参数
    # 			"type": "object", # 固定使用 type: object 来使 Kimi 大模型生成一个 JSON Object 参数
    # 			"required": ["url"], # 使用 required 字段告诉 Kimi 大模型哪些参数是必填项
    # 			"properties": { # properties 中是具体的参数定义，你可以定义多个参数
    # 				"url": { # 在这里，key 是参数名称，value 是参数的具体定义
    # 					"type": "string", # 使用 type 定义参数类型
    # 					"description": """
    # 						需要获取内容的网站地址（URL），通常情况下从搜索结果中可以获取网站的地址。
    # 					""" # 使用 description 描述参数以便 Kimi 大模型更好地生成参数
    # 				}
    # 			}
    # 		}
    # 	}
    # }
]


def chat(input: str) -> str:
    """
    chat 函数支持多轮对话，每次调用 chat 函数与 Kimi 大模型对话时，Kimi 大模型都会”看到“此前已经
    产生的历史对话消息，换句话说，Kimi 大模型拥有了记忆。
    """

    # 携带 messages 与 Kimi 大模型对话
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=make_messages(input),
        temperature=0.3,
        tools=tools,
    )

    # 通过 API 我们获得了 Kimi 大模型给予我们的回复消息（role=assistant）


    assistant_message = completion.choices[0].message

    # 为了让 Kimi 大模型拥有完整的记忆，我们必须将 Kimi 大模型返回给我们的消息也添加到 messages 中
    messages.append(assistant_message)

    return assistant_message.content

print(chat("你好，我今年 27 岁。"))
print(chat("你知道我今年几岁吗？"))  # 在这里，Kimi 大模型根据此前的上下文信息，将会知道你今年的年龄是 27 岁



















