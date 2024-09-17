import sys
import time
import threading
from queue import Queue

# 创建一个队列用于存储输出内容
response_queue = Queue()

def output_thread():
    while True:
        if not response_queue.empty():
            # 获取队列中的输出内容
            response_part = response_queue.get()
            sys.stdout.write(response_part)
            sys.stdout.flush()
            time.sleep(0.01)  # 控制输出速度
            response_queue.task_done() # 标记任务完成

def print_progress(last_response, response, max_length=100000):
    # 将新的输出内容放入队列
    response_update = f"{response.replace(last_response, '')}"
    response_queue.put(response_update)

# 启动输出线程
output_thread = threading.Thread(target=output_thread)
output_thread.daemon = True
output_thread.start()

# 示例使用
last_response = ""
response = "Hello, world!"
response_list = ["如果你的函数调用非常快，而你希望输出能够慢于函","如果你的函数调用非常快，而你希望输出能够慢于函数调用的速度","如果你的函数调用非常快，而你希望输出能够慢于函数调用的速度，并且希望能够有一个缓冲机制来逐步输出，那么你可","如果你的函数调用非常快，而你希望输出能够慢于函数调用的速度，并且希望能够有一个缓冲机制来逐步输出，那么你可以考虑以下几个方案："]
for response in response_list:
    for i in range(len(response) + 1):
        print_progress(last_response, response[:i + 1])
        last_response = response[:i + 1]
        # 主线程可以继续执行其他任务，输出由输出线程控制
        time.sleep(0.01)  # 控制主线程的调用速度

# time.sleep(100)
# 等待队列中的所有任务完成
response_queue.join()
print("ok")