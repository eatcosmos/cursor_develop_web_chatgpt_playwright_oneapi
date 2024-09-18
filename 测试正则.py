import mdformat
response = '当然，下面是一个简单的 C++ 冒泡排序算法的实现代码示例。此示例将演示如何对整数数组进行排序，并输出排序结果。\n\n### 冒泡排序 C++ 代码\n    \n    \n    cpp\n    \n    复制代码\n    \n    #include <iostream>\n    using namespace std;\n    \n    // 冒泡排序函数\n    void bubbleSort(int arr[], int n) {\n        bool swapped;\n        for (int i = 0; i < n - 1; i++) {\n            swapped = false;\n            // 遍历数组的未排序部分\n            for (int j = 0; j < n - i - 1; j++) {\n                if (arr[j] > arr[j + 1]) {\n    \n'
# response = '你运行的命令是用于在 `gpt` 虚拟环境中使用 Python 解释器执行脚本 `test_chatgpt_interaction.py`。具 体执行步骤如下：\n\n### 执行步骤\n\n  1. **打开 PowerShell** ：\n\n     * 在 Windows 中按 `Win + X`，选择“Windows PowerShell”或“Windows Terminal”。\n  2. **输入并执行命令** ：\n\n     * 在 PowerShell 中输入以下命令并按 `Enter`：\n        \n                powershell\n        \n        复制代码\n        \n        & C:/Users/dcsco/anaconda3/envs/gpt/python.exe c:/Code/Cursor/cursor_develop_web_chatgpt_playwright_oneapi/test_chatgpt_interaction.py\n        \n\n### 可能遇到的问题及解决方案\n\n  1. **Python 环境问题** ：\n\n     * 确保 Anaconda 中已经安装并激活了名为 `gpt` 的虚拟环境。你可以 通过以下命令查看已创建的环境：\n        \n                bash\n        \n        复制代码\n        \n        conda info --envs\n        \n\n     * 如果环境中缺少必要的依赖库，使用 `conda install`  或 `pip install` 安装相关库。\n  2. **路径问题** ：\n\n     * 确保路径 `c:/Code/Cursor/cursor_develop_web_chatgpt_playwright_oneapi/test_chatgpt_interaction.py` 是正确的，文件存在且可访问。\n  3. **脚本权限** ：\n\n     * 如果出现权限问题，确保你有足够的权限执行该脚本，或在 PowerShell 以管理员模 式运行。\n\n### 验证环境是否正确\n\n你可以在运行脚本前，先检查 Python 版本和路径是否正确：\n    \n    \n    powershell\n    \n    复制代码\n    \n    & C:/Users/dcsco/anaconda3/envs/gpt/python.exe --version\n    \n\n如果有任何错误提示，请将具体错误贴出来，我可以进一步帮助你解决。\n'

import re

print("\n回复完成")
response = re.sub(r'\n {4,}\n\n', '\n```\n\n', response)
response = re.sub(r'\n {4,}\n$', '\n```\n\n', response)
# response = re.sub(r'\n {4,}', '\n', response) # 去除代码多余空格
#
response = re.sub(r'\n {4,}\n {4,}([a-zA-Z]{1,})\n {4,}\n {4,}复制代码\n {4,}', '\n\n```\\1\n', response)
response = re.sub(r'\n {4,}\n {4,}\n {0,}复制代码\n {4,}', '\n\n```\n', response)

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
  
response = 处理代码块(response)
response = re.sub(r'(\n{3,})', '\n\n', response) # 去除多余换行符
import mdformat
response = mdformat.text(response)

print(f"{response}")
print(repr(response))

