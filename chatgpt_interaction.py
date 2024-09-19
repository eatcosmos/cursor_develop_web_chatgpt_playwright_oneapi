import os
import re
import sys
import time
import logging
import html2text
import threading
from queue import Queue
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

input_box_locator = 'div[id="prompt-textarea"]'
send_button_selector = 'button[data-testid="send-button"]'
stop_button_selector = 'button[data-testid="stop-button"]'
regenerate_button_selector = 'div.flex.w-full.items-center.justify-center.gap-1\\.5'
feedback_div_locator = 'div.mt-1.flex.gap-3.empty\\:hidden.-ml-2'

def 处理换行(response):
    # 正则匹配符合 r'\n {4,}' 的字符串，然后替换这个字符串为 \n
    matchstr = re.search(r'\n {4,}', response)
    if matchstr:
        response = response.replace(matchstr.group(0), '\n')
    response = re.sub(r'^(([a-zA-Z]{0,})\n{1,})', '\\2\n', response)
    response = re.sub(r'(\n{1,}$)', '\n', response)
    return response

def 处理代码块(markdown_text):
    # 正则表达式匹配三个反引号包裹的代码块 (```code```)
    pattern = re.compile(r'```(.*?)```', re.DOTALL)
    # 替换每个代码块，进行格式化处理
    def replace_code_block(match):
        code_block = match.group(1) # 获取代码块内容并去除首尾空白
        formatted_code = 处理换行(code_block)  # 调用格式化函数
        return f'```{formatted_code}```'  # 用格式化后的代码块替换
    # 使用 sub 方法进行替换
    formatted_markdown = re.sub(pattern, replace_code_block, markdown_text)
    return formatted_markdown
class ChatGPTInteraction:     
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        # # 
        self.response_queue = Queue()
        # # 
        # self.stream_output_thread = threading.Thread(target=self.stream_output_thread)
        # self.stream_output_thread.daemon = True
        # self.stream_output_thread.start()

    def connect_to_browser(self):
        if not self.playwright:
            self.playwright = sync_playwright().start()

        if not self.browser:
            print("连接到已打开的 Edge 浏览器...")
            try:
                self.browser = self.playwright.chromium.connect_over_cdp(
                    "http://localhost:9222")
                print("成功连接到浏览器")
            except Exception as e:
                print(f"连接到浏览器时出错: {e}")
                raise

        if not self.page:
            print("查找 ChatGPT 标签页...")
            for page in self.browser.contexts[0].pages:
                if "https://chatgpt.com" in page.url:
                    self.page = page
                    print(f"找到 ChatGPT 页面: {self.page.url}")
                    # 等待刷新完成
                    self.等待刷新完成()
                    time.sleep(1)
                    break

            if not self.page:
                raise Exception("未找到 ChatGPT 页面，请确保已经打开并登录了 chat.openai.com")

    def html_to_markdown(self, html_content):
        h = html2text.HTML2Text()
        h.ignore_links = False
        h.ignore_images = False
        h.ignore_emphasis = False
        h.body_width = 0  # 不自动换行
        return h.handle(html_content)

    def stream_output_thread(self):
        while True:
            if not self.response_queue.empty():
                response_part = self.response_queue.get()
                for i in range(len(response_part)):
                    sys.stdout.write(response_part[i])
                    sys.stdout.flush()
                    time.sleep(0.01)  # 控制输出速度
                self.response_queue.task_done()

    def click_regenerate_button(self):
        try:
            # 等待按钮出现
            button = self.page.wait_for_selector(regenerate_button_selector, timeout=5000)
            
            # 检查按钮是否包含正确的 SVG 图标
            svg = button.query_selector('svg')
            if svg:
                path = svg.query_selector('path')
                if path:
                    d_attribute = path.get_attribute('d')
                    if d_attribute and d_attribute.startswith('M4.47189 2.5C5.02418 2.5 5.47189 2.94772'):
                        # 点击按钮
                        button.click()
                        print("重新生成按钮已点击")
                        return True 
            print("未找到匹配的重新生成按钮")
            return False
        except TimeoutError:
            print("等待重新生成按钮超时")
            return False
    # 根据输入框是否存在，判断等待刷新完成
    def 等待刷新完成(self):
        self.page.reload()
        while True:
            try:
                input_box = self.page.locator(input_box_locator)
                if input_box.count() > 0:
                    print("刷新完成")
                    break
                print("等待刷新...")
                time.sleep(1)
            except:
                pass
    def 发送按钮已经激活(self):
        try:
            # 定位发送按钮            
            # 等待按钮出现，最多等待1秒
            # send_button = self.page.wait_for_selector(send_button_selector, state='attached', timeout=1000)
            send_button = self.page.locator(send_button_selector)
            if send_button:
                # 检查按钮是否被禁用
                is_disabled = send_button.get_attribute('disabled') is not None
                
                if is_disabled:
                    logger.info("发送按钮当前被禁用")
                    return False
                else:
                    logger.info("发送按钮当前可用")
                    return True
            else:
                logger.warning("未找到发送按钮")
                return False
        except Exception as e:
            logger.exception("检查发送按钮状态时出错: %s", str(e))
            return False
    def 流式传输激活(self):
        try:
            # 等待发送按钮变成"停止流式传输"按钮
            # 等待按钮出现，最多等待10秒
            # self.page.wait_for_selector(stop_button_selector, state='attached', timeout=10000)
            
            # 如果找到了"停止流式传输"按钮，说明回复正在生成
            stop_button = self.page.query_selector(stop_button_selector)
            if stop_button:
                # logger.info("回复正在生成")
                return True
            else:
                # logger.warning("未检测到回复生成")
                return False
        except Exception as e:
            logger.exception("等待流式传输激活时出错: %s", str(e))
            return False

    def interact_with_chatgpt(self, question):
        self.connect_to_browser()
        while True:
            print(f"\n输入问题: {question}")
            input_box = self.page.locator(input_box_locator)
            input_box.fill(question)
            time.sleep(0.3) # 等待操作完成
            #
            if self.发送按钮已经激活():
                print(f"发送按钮已经激活")
                send_button = self.page.locator('button[data-testid="send-button"]')
                print(f"点击发送")
                send_button.click()
                time.sleep(0.3) # 等待操作完成
                流式传输激活 = False
                start_time = time.time()
                timeout = 60  # 设置30秒超时
                while True:
                    # 假设点击发送肯定成功
                    if self.流式传输激活():
                        print(f"流式传输激活")
                        流式传输激活 = True
                        break
                    else:
                        # print(f"流式传输未激活")
                        time.sleep(0.1)
                    if time.time() - start_time > timeout:
                        print(f"流式传输超时")
                        break
                if 流式传输激活:
                    break
            else:
                print(f"发送按钮无法激活")
                self.等待刷新完成()

        print("等待流式传输...")
        response = ""
        # 清空 response_queue
        # self.response_queue.queue.clear()
        start_time = time.time()
        while True:
            try:
                while True:
                    try:
                        last_article = self.page.locator('article:last-child')
                        new_content_html =      last_article.locator('div.markdown').inner_html()
                        break
                    except Exception as e:
                        # print(f"获取新内容时出错: {e}")
                        time.sleep(0.1)
                new_content_markdown = self.html_to_markdown(new_content_html)
                # print(f"new_content_markdown: {new_content_markdown}")
                # print(f"response: {response}")
                if new_content_markdown != response:
                    # response_update = f"{new_content_markdown.replace(response, '')}"
                    # if new_content_markdown == response_update:
                    #     response_update = f"{new_content_markdown.replace(response[:-1], '')}"
                    # response_update = f"{new_content_markdown.replace(response[:-1], '')}"
                    # response_update = response_update[:-1]
                    # self.response_queue.put(response_update)
                    response = new_content_markdown
                    # print(f"部分回复 (长度: {len(response)}): {response[:100]}...")
                    time.sleep(0.1)
                else:
                    if not self.流式传输激活():
                        # print(f"流式传输结束")
                        break
                    if time.time() - start_time > 60:  # 60秒超时
                        print("\n回复超时")
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"\n回复出错: {e}")
                if time.time() - start_time > 60:  # 60秒超时
                    print("\n回复超时")
                    break
                time.sleep(0.1)
        # self.response_queue.join()  # 等待队列中的所有任务完成
        print("流式传输完成：\n")
        # self.等待刷新完成() # 发送按钮无法激活时才刷新
        #
        response = re.sub(r'\n {4,}\n\n', '\n```\n\n', response)
        response = re.sub(r'\n {4,}\n$', '\n```\n\n', response)
        # response = re.sub(r'\n {4,}', '\n', response) # 去除代码多余空格
        #
        response = re.sub(r'\n {4,}\n {4,}([a-zA-Z]{1,})\n {4,}\n {4,}复制代码\n {4,}', '\n\n```\\1\n', response)
        response = re.sub(r'\n {4,}\n {4,}\n {0,}复制代码\n {4,}', '\n\n```\n', response)
        #
        response = 处理代码块(response)
        response = re.sub(r'(\n{3,})', '\n\n', response) # 去除多余换行符
        import mdformat
        response = mdformat.text(response)      
        # print(f"{response}")
        # print(repr(response))
        # 以字符串形式打印，比如换行的要打印为 \n
        
        return response.strip()

    def close(self):
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


# 使用示例
if __name__ == "__main__":
    chat_interaction = ChatGPTInteraction()
    try:
        # time.sleep(1)
        while True:
            # 先清理终端
            # os.system('cls' if os.name == 'nt' else 'clear') # 没用
            question = input("\n请输入您的问题（输入 'quit' 退出）: ")
            if question.lower() == 'quit' or question.lower() == 'q':
                break
            response = chat_interaction.interact_with_chatgpt(question)
            print(response)
    finally:
        chat_interaction.close()
