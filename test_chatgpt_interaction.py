from chatgpt_interaction import ChatGPTInteraction

def main():
    chat_interaction = ChatGPTInteraction()
    try:
        while True:
            question = input("\n请输入您的问题（输入 'quit' 退出）: ")
            if question.lower() == 'quit':
                break
            response = chat_interaction.interact_with_chatgpt(question)
            # print(response)
    finally:
        chat_interaction.close()

if __name__ == "__main__":
    main()
