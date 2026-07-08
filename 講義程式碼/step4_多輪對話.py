import requests
from dotenv import dotenv_values

s = dotenv_values(".env")
url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}

messages = [{"role": "system", "content": "你是友善的小助理，請用繁體中文簡短回答。"}]

def ask(text):
    messages.append({"role": "user", "content": text})
    body = {"model": s["LLM_MODEL"], "messages": messages}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    reply = r.json()["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})
    return reply

while True:
    try:
        user = input("你 > ")
    except EOFError:
        break
    if user == "/exit":
        break
    print("AI >", ask(user))
