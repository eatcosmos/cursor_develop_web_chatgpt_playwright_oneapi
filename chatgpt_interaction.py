import os
import re
import sys
import time
import html2text
from playwright.sync_api import sync_playwright

def find_chatgpt_page(context):
    print("开始查找 ChatGPT 标签页...")
    for page in context.pages:
        print(f"检查页面: {page.url} - 标题: {page.title()}")
        if "https://chatgpt.com" in page.url:
            print(f"找到 ChatGPT 页面: {page.url}")
            return page
    print("未找到 ChatGPT 页面")
    return None

def html_to_markdown(html_content):
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.ignore_emphasis = False
    h.body_width = 0  # 不自动换行
    return h.handle(html_content)
  
def interact_with_chatgpt(question):
    with sync_playwright() as p:
        print("连接到已打开的 Edge 浏览器...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("成功连接到浏览器")
        except Exception as e:
            print(f"连接到浏览器时出错: {e}")
            raise

        print("获取浏览器上下文...")
        context = browser.contexts[0]  # 假设只有一个上下文
        print(f"找到 {len(context.pages)} 个页面")

        print("查找 ChatGPT 标签页...")
        page = find_chatgpt_page(context)
        if not page:
            raise Exception("未找到 ChatGPT 页面，请确保已经打开并登录了 chatgpt.com")

        print(f"在输入框中输入问题: {question}")
        input_box = page.locator('div[id="prompt-textarea"]')
        input_box.fill(question)

        print("点击发送按钮")
        send_button = page.locator('button[data-testid="send-button"]')
        send_button.click()
        # time.sleep(1)
        while True:
            last_article = page.locator('article:last-child')
            feedback_div = last_article.locator('div.mt-1.flex.gap-3.empty\\:hidden.-ml-2')
            if feedback_div.count() > 0:
                print("检测到反馈标签...")
                time.sleep(0.1)
            else:
                break
        
        print("等待回复生成...")
        response = ""
        start_time = time.time()
        while True:
            last_article = page.locator('article:last-child')
            new_content_html = last_article.locator('div.markdown').inner_html()
            new_content_markdown = html_to_markdown(new_content_html)
                
            if new_content_markdown != response:
                response = new_content_markdown
                print(f"部分回复 (长度: {len(response)}): {response[:100]}...")
                time.sleep(0.1) # 0.1秒更新一次
            else:
                # 检查是否出现反馈标签
                feedback_div = last_article.locator('div.mt-1.flex.gap-3.empty\\:hidden.-ml-2')
                if feedback_div.count() > 0:
                    print("检测到反馈标签，回复完成")
                    break
                if time.time() - start_time > 60:  # 60秒超时
                    print("回复生成超时")
                    break
                time.sleep(0.5)

        print("回复完成")
        return response