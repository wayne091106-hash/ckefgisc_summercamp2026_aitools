import requests, json, re
from dotenv import dotenv_values

s = dotenv_values(".env")
url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}
MAX_STEPS = 8

def web_search(query):
    key = s.get("TAVILY_API_KEY", "")
    if not key:
        return "沒有設定 TAVILY_API_KEY，不能搜尋。"
    r = requests.post("https://api.tavily.com/search",
                      headers={"Authorization": "Bearer " + key},
                      json={"query": query, "max_results": 3, "include_answer": True},
                      timeout=30)
    data = r.json()
    out = []
    if data.get("answer"):
        out.append("摘要：" + data["answer"])
    for it in data.get("results", []):
        out.append(it.get("title", "") + "\n" + it.get("content", "")[:200])
    return "\n\n".join(out)

def run_tool(action):
    if action["tool"] == "web_search":
        return web_search(action["args"]["query"])
    return "未知工具：" + str(action.get("tool"))

def call_model(messages):
    body = {"model": s["LLM_MODEL"], "messages": messages}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    return r.json()["choices"][0]["message"]["content"]

def find_action(text):
    blocks = re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL) or [text]
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError:
            continue
        if "tool" in data:
            return data
    return None

SYSTEM = '''你是小智慧體，請用繁體中文。
遇到今天、最新、即時、新聞、股價這類即時資訊，一定要先用 web_search 查，不可以憑記憶回答：
```json {"tool":"web_search","args":{"query":"關鍵字"}} ```
要用工具時只輸出 JSON、不要多話；不用工具就直接回答。'''

messages = [{"role": "system", "content": SYSTEM}]

def agent(user_text):
    messages.append({"role": "user", "content": user_text})
    for i in range(MAX_STEPS):
        ai_text = call_model(messages)
        action = find_action(ai_text)
        if action is None:
            messages.append({"role": "assistant", "content": ai_text})
            return ai_text
        messages.append({"role": "assistant", "content": ai_text})
        print("  （動作：" + json.dumps(action, ensure_ascii=False) + "）")
        result = run_tool(action)
        messages.append({"role": "user", "content": "工具結果：\n" + result})
    return "步數太多，先停下來。"

while True:
    try:
        user = input("你 > ")
    except EOFError:
        break
    if user == "/exit":
        break
    print("AI >", agent(user))
