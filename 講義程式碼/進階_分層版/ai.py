import json
import re
from datetime import datetime

import requests

from tools import run_terminal, web_search


MAX_TOOL_CALLS = 20


SYSTEM_PROMPT = """
你是一個教學用的終端機小智慧體。

現在時間：__NOW__
工作區：__WORKSPACE__

你有兩個工具：
1. web_search：搜尋最新網路資料
2. terminal：在 Windows PowerShell 的工作區執行指令

重要規則：
- 使用繁體中文。
- 今天、現在、最新、即時資料，請先用 web_search。
- terminal 已經在工作區裡，不要寫 workspace/file.txt，直接寫 file.txt。
- 這是 Windows PowerShell，不是 Linux。不要使用 cat << EOF。
- 檔案已自動用 UTF-8 存檔，中文不會亂碼，你不用自己加 -Encoding 參數。
- 做報表、整理資料時，優先存成 .txt 或 .csv，最單純也最穩。
- 要執行 Python 時，一律用 py，不要用 python（python 可能指到錯的版本、找不到套件）。
- 安裝套件用：py -m pip install 套件名。
- 需要做 Excel(.xlsx) 或 Word(.docx) 時，先寫一個 .py 檔（可用 pandas、openpyxl、python-docx），再用 py 檔名.py 執行它。
- 如果使用者明確要求建立、寫入、修改檔案，第一個 terminal 指令就直接完成，不要先檢查或反問。
- 工具執行成功後，請簡短告訴使用者你做了什麼。
- 每次只使用一個工具。
- 如果不用工具，就直接回答。
- 如果要用工具，只輸出 JSON，不要加解釋文字。

搜尋格式：
```json
{"tool":"web_search","args":{"query":"搜尋關鍵字"}}
```

終端機格式：
```json
{"tool":"terminal","args":{"command":"PowerShell 指令"}}
```

建立並讀取檔案的例子：
```json
{"tool":"terminal","args":{"command":"Set-Content -Path hello.txt -Value \"Hello\"; Get-Content hello.txt"}}
```
"""


def ask_ai(messages, user_text, settings):
    if len(messages) == 0:
        messages.append({
            "role": "system",
            "content": make_system_prompt(settings),
        })

    messages.append({
        "role": "user",
        "content": "本次訊息時間：" + now() + "\n使用者：" + user_text,
    })

    for i in range(MAX_TOOL_CALLS):
        ai_text = call_model(messages, settings)
        tool_call = find_tool_call(ai_text)

        if tool_call is None:
            messages.append({"role": "assistant", "content": ai_text})
            return ai_text

        messages.append({"role": "assistant", "content": ai_text})

        print("\n第 " + str(i + 1) + " 次工具調用")
        print("模型決定：")
        print(ai_text)

        try:
            result = run_tool(tool_call, settings)
        except Exception as e:
            result = (
                "工具執行失敗：" + str(e) +
                "。請確認格式是 {\"tool\":...,\"args\":{...}}，重新輸出一次。"
            )

        print("\n工具結果：")
        print(result)

        messages.append({
            "role": "user",
            "content": "工具結果如下，請根據結果繼續：\n" + result,
        })

    return "工具使用太多次，先停下來。"


def make_system_prompt(settings):
    prompt = SYSTEM_PROMPT.replace("__NOW__", now())
    prompt = prompt.replace("__WORKSPACE__", settings.get("WORKSPACE_DIR", "workspace"))
    return prompt


def now():
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def call_model(messages, settings):
    url = settings["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
    headers = {
        "Authorization": "Bearer " + settings["LLM_API_KEY"],
        "Content-Type": "application/json",
    }
    data = {
        "model": settings["LLM_MODEL"],
        "messages": messages,
        "temperature": 0.2,
        "max_tokens": 2000,
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        body = response.json()
    except requests.exceptions.RequestException as e:
        return "（呼叫模型失敗，稍等幾秒再試一次：" + str(e) + "）"
    except ValueError:
        return "（呼叫模型失敗，稍等幾秒再試一次：伺服器回應不是合法的 JSON，狀態碼 " + str(response.status_code) + "）"

    if "choices" not in body:
        # 額度用完、伺服器忙碌時常見（例如 429），回應格式跟平常不一樣，這裡不要硬拆。
        return "（呼叫模型失敗，稍等幾秒再試一次：" + str(body) + "）"

    message = body["choices"][0]["message"]
    return message.get("content") or message.get("reasoning_content") or ""


def find_tool_call(text):
    json_blocks = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.DOTALL)
    json_blocks += re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", text, flags=re.DOTALL)

    if len(json_blocks) == 0:
        json_blocks = [text.strip()]

    for block in json_blocks:
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue

        if "tool" in data and "args" in data:
            return data

    return None


def run_tool(tool_call, settings):
    tool_name = tool_call["tool"]
    args = tool_call["args"]

    if tool_name == "web_search":
        return web_search(args.get("query", ""), settings.get("TAVILY_API_KEY", ""))

    if tool_name == "terminal":
        return run_terminal(args.get("command", ""), settings.get("WORKSPACE_DIR", "workspace"))

    return "未知工具：" + tool_name
