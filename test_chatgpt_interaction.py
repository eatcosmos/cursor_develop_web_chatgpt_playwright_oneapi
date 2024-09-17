import sys
import time
from chatgpt_interaction import interact_with_chatgpt

def print_progress():
    chars = "|/-\\"
    for _ in range(20):  # 显示进度 5 秒
        for char in chars:
            sys.stdout.write(f'\r处理中 {char}')
            sys.stdout.flush()
            time.sleep(0.25)

def main():
    print("欢迎使用 ChatGPT 交互测试程序")
    print("输入 'quit' 或 'exit' 来退出程序")

    while True:
        try:
            user_input = input("\n请输入您的问题: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("感谢使用，再见！")
                break

            if not user_input:
                print("输入不能为空，请重新输入。")
                continue

            print("正在处理您的问题，请稍候...")
            # print_progress()  # 添加进度指示
            response = interact_with_chatgpt(user_input)
            print("\nChatGPT 的回答:")
            print(response)

        except KeyboardInterrupt:
            print("\n程序被用户中断。")
            break
        except Exception as e:
            print(f"发生错误: {e}")
            print("请检查您的网络连接和浏览器状态，然后重试。")

if __name__ == "__main__":
    main()