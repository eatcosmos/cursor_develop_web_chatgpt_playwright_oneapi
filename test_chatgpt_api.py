# https://api.aiproxy.io
# sk-
from openai import OpenAI

# 从 api_key.txt 中读取 API 密钥
with open('api_key.txt', 'r') as file:
    api_key = file.read().strip()
    print(api_key[:10])

client = OpenAI(
    # #将这里换成你在aiproxy api keys拿到的密钥
    api_key=api_key,
    # 这里将官方的接口访问地址，替换成aiproxy的入口地址
    base_url="http://127.0.0.1:5000/v1"
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "冒泡算法 python 代码",
        }
    ],
    model="gpt-3.5-turbo",
)

print(chat_completion)
# ChatCompletion(id='chatcmpl-A8Vm0G0Fl5amwz3T9FD95w1hnKMdo', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Sure, here is a simple hello world Python code:\n\n```\nprint("Hello, World!")\n```', refusal=None, role='assistant', function_call=None, tool_calls=None), delta=None)], created=1726592124, model='gpt-3.5-turbo-0125', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=20, prompt_tokens=13, total_tokens=33, completion_tokens_details=None))

# curl https://api.aiproxy.io/v1/chat/completions \
#   -H "Content-Type: application/json" \
#   -H "Authorization: Bearer sk-uey7n8Io0b5VeCgqvTfVuw1hgc8tCMLyJ8JjoAjttOaCHGPr" \
#   -d '{
#     "model": "gpt-3.5-turbo",
#     "messages": [
#         {
#             "role": "user",
#             "content": "冒泡算法 C++ 代码，给出 3 种。"
#         }
#     ]
#   }'