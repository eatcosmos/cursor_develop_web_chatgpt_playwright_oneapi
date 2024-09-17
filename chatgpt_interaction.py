import os
import re
import sys
import time
import html2text
import threading
from queue import Queue
from playwright.sync_api import sync_playwright


input_box_locator = 'div[id="prompt-textarea"]'
def 处理换行(response):
    # 正则匹配符合 r'\n {4,}' 的字符串，然后替换这个字符串为 \n
    matchstr = re.search(r'\n {4,}', response)
    if matchstr:
        response = response.replace(matchstr.group(0), '\n')
    response = re.sub(r'(^\n{1,})', '\n', response)
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
                    self.page.reload() # 刷新页面
                    # 等待刷新完成
                    self.等待刷新完成()
                    time.sleep(1)
                    break

            if not self.page:
                raise Exception("未找到 ChatGPT 页面，请确保已经打开并登录了 chat.openai.com")
        # if not self.browser:
        #     print("启动 Edge 浏览器...")
        #     try:
        #         self.browser = self.playwright.chromium.launch_persistent_context(
        #             user_data_dir="./user_data",
        #             channel="msedge",
        #             headless=False,
        #             args=["--start-maximized"]
        #         )
        #         print("成功启动浏览器")
        #     except Exception as e:
        #         print(f"启动浏览器时出错: {e}")
        #         raise

        # if not self.page:
        #     print("打开 ChatGPT 页面...")
        #     self.page = self.browser.new_page()
        #     self.page.goto("https://chatgpt.com")
        #     print(f"已打开 ChatGPT 页面: {self.page.url}")

        # # 等待页面加载完成
        # # self.page.wait_for_load_state("networkidle")

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
        # 定位按钮
        button_selector = 'div.flex.w-full.items-center.justify-center.gap-1\\.5'
        
        try:
            # 等待按钮出现
            button = self.page.wait_for_selector(button_selector, timeout=5000)
            
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
        while True:
            try:
                input_box = self.page.locator(input_box_locator)
                if input_box.count() > 0:
                    break
                print("等待刷新完成...")
                time.sleep(1)
            except:
                pass
    def interact_with_chatgpt(self, question):
        self.connect_to_browser()
        while True:
            try:
                print(f"输入问题: {question}")
                input_box = self.page.locator(input_box_locator)
                input_box.fill(question)
                time.sleep(0.3)
                
                print("点击发送")
                send_button = self.page.locator('button[data-testid="send-button"]')
                send_button.click()
                print(f"发送成功")
                break
            except:
                # 刷新网页
                self.page.reload()
                self.等待刷新完成()
                continue
        # 等待回复开始
        feedback_div_locator = 'div.mt-1.flex.gap-3.empty\\:hidden.-ml-2'
        while True:
            last_article = self.page.locator('article:last-child')
            feedback_div = last_article.locator(feedback_div_locator)
            if feedback_div.count() > 0:
                # print("检测到反馈标签...")
                time.sleep(0.1)
            else:
                print("回复激活...")
                break

        print("等待回复...")
        response = ""
        # 清空 response_queue
        self.response_queue.queue.clear()
        start_time = time.time()
        while True:
            try:
                last_article = self.page.locator('article:last-child')
                new_content_html = last_article.locator(
                    'div.markdown').inner_html()
                new_content_markdown = self.html_to_markdown(new_content_html)

                if new_content_markdown != response:
                    # print(f"new_content_markdown: {new_content_markdown}")
                    # print(f"response: {response}")
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
                    feedback_div = last_article.locator(feedback_div_locator)
                    if feedback_div.count() > 0:
                        # print("\n检测到反馈标签，回复完成")
                        break
                    if time.time() - start_time > 60:  # 60秒超时
                        print("\n回复生成超时")
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"\n提取回复时出错: {e}")
                if time.time() - start_time > 60:  # 60秒超时
                    print("\n回复生成超时")
                    break
                time.sleep(0.1)
        # self.response_queue.join()  # 等待队列中的所有任务完成
        print("\n回复完成")
        self.page.reload() # 刷新页面
        self.等待刷新完成()
        #
        response = re.sub(r'\n {4,}\n\n', '\n```\n\n', response)
        response = re.sub(r'\n {4,}\n$', '\n```\n\n', response)
        # response = re.sub(r'\n {4,}', '\n', response) # 去除代码多余空格
        #
        response = re.sub(r'\n {4,}\n {4,}[a-zA-Z]{1,}\n {4,}\n {4,}复制代码\n {4,}', '\n\n```\n', response)
        response = re.sub(r'\n {4,}\n {4,}\n {0,}复制代码\n {4,}', '\n\n```\n', response)
        #
        response = 处理代码块(response)
        response = re.sub(r'(\n{3,})', '\n\n', response) # 去除多余换行符
        import mdformat
        response = mdformat.text(response)      
        print(f"{response}")
        print(repr(response))
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
        while True:
            question = input("请输入您的问题（输入 'quit' 退出）: ")
            if question.lower() == 'quit' or question.lower() == 'q':
                break
            response = chat_interaction.interact_with_chatgpt(question)
            print(response)
    finally:
        chat_interaction.close()
