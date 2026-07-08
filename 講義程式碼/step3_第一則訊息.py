import requests
from dotenv import dotenv_values

s = dotenv_values(".env")

def ask(text):
    url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
    headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}
    body = {
        "model": s["LLM_MODEL"],
        "messages": [{"role": "user", "content": text}],
    }
    r = requests.post(url, headers=headers, json=body, timeout=60)
    data = r.json()
    reply = data["choices"][0]["message"]["content"]
    return reply

print(ask("用一句話介紹 Python"))
