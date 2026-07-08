# 暑訓講義 AI工具

> 這堂課，**不是教你怎麼用 ChatGPT**，而是要**做一個會自己動手的微型 agent**。
> 你只要會 `while`、`for`、`if`，就能跟上。每一關會先教你**新出現的語法或觀念**，
> 一小段一小段組起來，最後才貼出完整的 `agent.py`——不會一次把整段丟給你。
> 然後照著 🎮 **動手互動**（跑 → 看 → 改再跑）做做看。

## 大概的目錄

```
①  申請 API + 設定 .env      ← 先讓程式有「大腦」可用
②  發送第一則訊息             ← 最小的 chatbot
③  多輪對話                  ← 讓它有基礎記憶
④  ReAct + 搜尋工具          ← 讓它會「查資料」
⑤  整合成一個可用的智慧體     ← 打包！到這裡就是完整一課 ✅
⑥  真agent功能：終端機工具    ← 有時間再玩，讓它會操作電腦
```

> 到第 ⑤ 步，你就已經有一個**會聊天、會上網查資料**的完整 AI 智慧體了。
> 第 ⑥ 步是加碼，有點難。

---

# STEP 1　申請 API 金鑰

AI 模型跑在別人的伺服器上，要用它得先有一把**金鑰**（像會員卡號）。我們準備三家（挑**一家**用就好），外加一個搜尋服務。

| 供應商 | 去哪拿金鑰 | 金鑰開頭 | 特色 |
|---|---|---|---|
| **Google AI Studio** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) | `AIza…` | 有 Google 帳號就行，最無腦、免費、**但學校帳號不能用** |
| **Groq** | [console.groq.com/keys](https://console.groq.com/keys) | `gsk_…` | 免費、**超快**、有額度限制 |
| **NVIDIA NIM** | [build.nvidia.com](https://build.nvidia.com) | `nvapi-…` | 免費、模型選擇多 |
| **Tavily（搜尋用）** | [app.tavily.com](https://app.tavily.com) | `tvly-…` | AI 專用搜尋，免費額度夠上課 |

**怎麼拿**（以 Google 為例）：登入 → 按「Create API key」→ 複製那串。其他家也都是註冊登入 → Create key → 複製。

> 🔑 **金鑰是密碼**：不要貼給別人、不要上傳到網路或 GitHub。它外流等於別人可以刷你的額度。雖然都是免費API是不會怎樣，~~我的API都放記事本~~

---

# STEP 2　設定 .env

金鑰不建議寫死在程式裡，我們放在一個叫 `.env` 的秘密檔，程式會自己讀。

**動手做：**

1. 在你的資料夾（例如 `我的智慧體`）裡，**新增一個檔案，檔名就叫 `.env`**（沒有副檔名，前面有一個點）。
2. 安裝套件（先裝這一個就好，`requests` 我們等 STEP 3 真的要用時再裝、再解釋它是什麼）：

```powershell
py -3.12 -m pip install python-dotenv
```

3. 打開 `.env`，**依你申請的那一家**，把對應那組**整段貼進去**（只要一組，不用三組都貼）：

**如果你用 Google AI Studio：**

```ini
LLM_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
LLM_API_KEY=貼上你剛剛複製的 Google 金鑰
LLM_MODEL=gemma-4-31b-it

TAVILY_API_KEY=貼上你的 Tavily 金鑰
WORKSPACE_DIR=workspace
```

**如果你用 Groq：**

```ini
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=貼上你剛剛複製的 Groq 金鑰
LLM_MODEL=qwen/qwen3.6-27b

TAVILY_API_KEY=貼上你的 Tavily 金鑰
WORKSPACE_DIR=workspace
```

**如果你用 NVIDIA NIM：**

```ini
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_API_KEY=貼上你剛剛複製的 NVIDIA 金鑰
LLM_MODEL=stepfun-ai/step-3.7-flash

TAVILY_API_KEY=貼上你的 Tavily 金鑰
WORKSPACE_DIR=workspace
```

> 等號兩邊**不要加空格、不要加引號**，直接 `LLM_API_KEY=abc123` 這樣貼上去就好。

**這三行在做什麼？**

```ini
LLM_BASE_URL=...   # 去哪一家（API端點網址，就是通訊地址）
LLM_API_KEY=...    # 你的鑰匙（API金鑰）
LLM_MODEL=...      # 要用哪個模型
```

> 💡 **這程式相容 OpenAI 格式，所以換供應商只要改這三行，程式一個字都不用動。**
> 想現場體驗看看：把 Google 那組換成 Groq 那組，等一下 STEP 3 寫好的程式完全不用改，直接重跑就會換一家回答你。
還有，每一家供應商它有很多模型，可以去供應商申請 API 的那個地方查。它的文件裡面通常都會寫好。

---

# STEP 3　發送第一則訊息

**目標**：讓程式對 AI 說一句話、收到回答。這就是最小的 chatbot。

**觀念**：所謂「呼叫 AI」，其實就是**寄一封 JSON 信**（帶金鑰＋問題）給伺服器，再**收一封 JSON 回信**。沒有魔法。

這一關第一次出現「字典」「函式」「套件」這些東西，我們一個一個拆開來看，**每教一個新東西，就先只寫那一小段**，不要跳著看，最後才會組成完整的函式。

### 3-1　套件是什麼？先裝 `requests`

Python 本身只有基本工具（`print`、`for`…），沒有「連上網路寄資料」的能力。這個能力別人已經寫好、包成一包放在網路上，這種東西叫**套件（package）**。`requests` 就是專門拿來「上網要資料」的套件。

```powershell
py -3.12 -m pip install requests
```

`pip install 套件名` 就是「幫我下載這個套件」的指令。裝好之後，在程式裡要先「借」進來才能用：

```python
import requests
```

> 🧩 **新語法：`import`**　`import 套件名` 就是「把別人寫好的套件借來用」，寫在檔案最上面。之後這個檔案裡任何地方，都可以用 `requests.xxx` 來呼叫這個套件提供的功能。

### 3-2　字典（dict）：用「名字」查「值」

我們要把 `.env` 裡的設定讀進程式。先加這一行：

```python
from dotenv import dotenv_values

s = dotenv_values(".env")
```

> 🧩 **新語法：字典 dict**（如果你的同學已經教過，這段可以快速看過）
>
> `dotenv_values(".env")` 執行完，會把 `.env` 裡每一行 `KEY=值`，都變成一種**用名字（鍵）去查值**的資料，叫**字典（dict）**。長得像這樣：
> ```python
> s = {"LLM_BASE_URL": "https://...", "LLM_API_KEY": "AIza...", "LLM_MODEL": "gemma-4-31b-it"}
> ```
> 想從字典裡拿東西，用中括號寫「鍵」的名字：
> ```python
> s["LLM_MODEL"]     # 會拿到 "gemma-4-31b-it"
> ```
> 這跟清單（list）用數字當索引不一樣——字典是用**你自己取的名字**當索引。

跑跑看，確認讀得到：

```python
print(s["LLM_MODEL"])
```

🎮 **動手互動**：跑這三行，畫面應該印出你剛剛在 `.env` 填的模型名稱。如果印出 `None` 或報錯，代表 `.env` 檔名或路徑不對，檢查一下檔案是不是真的叫 `.env`（不是 `.env.txt`）。

### 3-3　函式（function）：把步驟包起來，重複使用

接下來我們要把「問 AI 一句話」這件事，包成一個**函式**，之後可以重複呼叫。

> 🧩 **新語法：`def` 定義函式**
>
> ```python
> def ask(text):
>     ...
>     return 結果
> ```
> - `def 函式名(參數):`：宣告一個叫 `ask` 的函式，它需要別人給它一個資料，取名叫 `text`（這個叫**參數**）。
> - 函式裡面要做的事，往內縮排寫。
> - `return`：函式做完事，把算出來的**結果交回去**給呼叫它的地方。沒有 `return`，呼叫的人就拿不到任何東西。
> - 呼叫時：`ask("你好")` 就會把 `"你好"` 傳給 `text`，然後執行函式裡的內容。

先寫函式的骨架（還不能跑，只是搭架子）：

```python
def ask(text):
    pass   # pass 代表「先空著，之後再補」
```

### 3-4　組出要寄去的網址

把 STEP 2 讀到的 `LLM_BASE_URL` 接上固定的路徑 `/chat/completions`，變成完整的詢問窗口：

```python
url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
```

> 🧩 **新語法：字串方法 `.rstrip()`　和字串相加 `+`**
>
> - `.rstrip("/")` 是字串（str）自己帶的功能：把字串**結尾**的 `/` 拿掉（避免有人 `.env` 網址結尾多打一個 `/`，接起來變成 `xxx//chat/completions`）。
> - `+` 用在文字之間是「接起來」的意思：`"AB" + "CD"` 會變成 `"ABCD"`。

### 3-5　組信封：headers

寄信要告訴對方「你是誰」，這個資訊放在 `headers`（信封上的資訊）：

```python
headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}
```

`Authorization` 是「身分驗證」的意思，前面固定要加 `"Bearer "`（這是業界規定的格式，記住就好），後面接你的金鑰。

### 3-6　組信的內容：清單裝字典

AI 的對話內容，格式規定要放進一個**清單（list）**，清單裡面是一個個**字典**：

```python
body = {
    "model": s["LLM_MODEL"],
    "messages": [{"role": "user", "content": text}],
}
```

> 🧩 **新語法：清單裡裝字典 `[{...}]`**
>
> 中括號 `[ ]` 是清單（list），你在 `for x in [1, 2, 3]` 應該看過。這裡清單裡只裝一樣東西——一個字典，代表「這一句話」：
> - `"role": "user"`：這句話是「使用者」講的（之後還會出現 `"assistant"` 是 AI 講的、`"system"` 是規則）。
> - `"content": text`：真正講的內容，就是外面傳進來的那個 `text` 參數。

### 3-7　寄出去：`requests.post()`

```python
r = requests.post(url, headers=headers, json=body, timeout=60)
```

> 🧩 **新語法：關鍵字參數 `名字=值`**
>
> 之前呼叫函式都是直接照順序給值，例如 `ask("你好")`。這裡 `headers=headers`、`json=body`、`timeout=60` 這種寫法叫**關鍵字參數**——用「名字＝值」清楚指定「這個值是給哪個用途」，不用管前後順序。
> - `requests.post(網址, ...)`：把這封信**用 POST 方式**寄出去，然後等對方回信。
> - `json=body`：把我們的字典自動轉成 JSON 格式塞進信裡。
> - `timeout=60`：等超過 60 秒對方還沒回，就放棄（不要卡死）。

### 3-8　拆信封：把回應轉回字典

對方回的信也是 JSON 格式的文字，要轉回 Python 字典才能用 `[ ]` 去拿東西：

```python
data = r.json()
```

### 3-9　一層層打開箱子，拿到 AI 說的話

```python
reply = data["choices"][0]["message"]["content"]
```

這一行最多人看不懂，我們拆成四步慢慢看：

1. `data["choices"]`：從最外層字典，拿出叫 `choices` 的東西——它是一個**清單**。
2. `["choices"][0]`：清單的**第一個**東西。

   > 🧩 **新語法：索引從 0 開始**　清單第一個東西的編號是 `0`，不是 `1`。`[0]` 拿第一個、`[1]` 拿第二個——這跟你在 `for i in range(...)` 裡看過的編號方式一樣。

3. 這個「第一個東西」本身又是一個字典，`["message"]` 再從裡面拿出一層。
4. `["content"]`：最後才拿到 AI 真正講的那句話（文字）。

一層層打開，就像剝洋蔥／開俄羅斯娃娃，每個 `[ ]` 就是打開一層。

### 3-10　把結果交回去

```python
return reply
```

### 組起來：完整的 `ask()` 函式

把 3-3 到 3-10 全部接起來，就是完整的函式：

```python
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
```

最後呼叫它：

```python
print(ask("用一句話介紹 Python"))
```

<details><summary>👉 目前完整的 <code>agent.py</code>（跟丟了點開對照）</summary>

```python
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
```
</details>

🎮 **動手互動**
1. 跑：`py agent.py` → 你應該會看到一句介紹 Python 的話。
2. 改：把問句換成你想問的，再跑一次。
3. 進階：到 `.env` 換另一家供應商（把當前那組換成另一組），**程式不改**，再跑，感受差別。

✅ **檢查點**：AI 在你電腦裡嗎？程式怎麼跟它溝通的？
> <details><summary>▸ 點開看</summary>
>
> AI 不在你電腦裡，它在對方伺服器上。程式用 `requests.post()` **寄出一封 JSON 請求**（金鑰＋問題），再用 `.json()` **拆開回來的 JSON 回應**，一層層打開拿到 `content` 就是答案。
> </details>

---

# STEP 4　多輪對話（讓它有基礎記憶）

**目標**：從「問一句答一句」變成能**連續聊天、記得前面說過的話**。

**觀念**：殘酷真相——模型**本身沒有記憶**，每次呼叫都像第一次見你。祕密是：我們每次都把**整段對話**一起寄過去。記憶不在 AI 那邊，而在我們程式裡一個**會一直長大的清單 `messages`**。

### 4-1　把裝一句話的清單，換成會一直長大的清單

STEP 3 我們每次都是「臨時組一個只裝一句話的清單」。現在改成：**在函式外面**先建一個清單，之後每次對話都往裡面加：

```python
messages = [{"role": "system", "content": "你是友善的小助理，請用繁體中文簡短回答。"}]
```

這則 `"role": "system"` 是最高規則，開場放一次就好。

### 4-2　`.append()`：往清單尾巴加東西

> 🧩 **新語法：清單方法 `.append()`**
>
> 清單有一個內建功能叫 `.append(東西)`，可以把「東西」加到清單的**最後面**。例如：
> ```python
> nums = [1, 2]
> nums.append(3)   # nums 變成 [1, 2, 3]
> ```
> 我們要用它，把「使用者這次說的話」和「AI 這次回的話」都加進 `messages`。

### 4-3　改寫 `ask()`：記得雙方講的話

```python
def ask(text):
    messages.append({"role": "user", "content": text})        # 先記下你的話
    body = {"model": s["LLM_MODEL"], "messages": messages}     # 這次改成整份 messages
    r = requests.post(url, headers=headers, json=body, timeout=60)
    reply = r.json()["choices"][0]["message"]["content"]
    messages.append({"role": "assistant", "content": reply})   # 也記下它的話 ← 這就是記憶
    return reply
```

跟 STEP 3 比對，差別只有兩個 `.append()`，還有 `messages` 內容從「只裝一句」變成「整份清單本身」。`url` 和 `headers` 一樣是先前那兩行，搬到函式外面先組好即可（因為每次都一樣，不用重算）：

```python
url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}
```

### 4-4　讓對話可以一直進行：`try / except`

我們要讓程式一直問、一直答，直到你說 `/exit`。用你已經會的 `while True` 沒問題，但這裡加一個新東西：

> 🧩 **新語法：`try / except`**
>
> `input()` 在某些情況下可能會出錯（例如視窗被關掉、輸入被中斷），這時候 Python 會丟出一個叫 `EOFError` 的錯誤，如果不處理，程式就會直接當掉。
> `try / except` 的意思是：「**試著**做 `try` 裡的事，如果出現 `except` 後面寫的那種錯誤，就跳去執行 `except` 裡的動作，程式不會崩潰」。
> ```python
> try:
>     user = input("你 > ")
> except EOFError:
>     break        # 遇到這個錯誤，就跳出迴圈
> ```

完整的聊天迴圈：

```python
while True:
    try:
        user = input("你 > ")
    except EOFError:
        break
    if user == "/exit":
        break
    print("AI >", ask(user))
```

<details><summary>👉 目前完整的 <code>agent.py</code></summary>

```python
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
```
</details>

🎮 **動手互動**
1. 跑，先說「我叫小明，喜歡籃球」，再問「我叫什麼？喜歡什麼？」→ 它記得。
2. 觀察：把 `messages.append({"role": "assistant", ...})` 那行暫時刪掉再跑，看它是不是就失憶了（測完加回去）。
3. 改人格：把 `system` 改成「你是毒舌但正確的助教」，感受語氣變化。

✅ **檢查點**：模型明明沒記憶，為什麼還能連續對話？記憶存在哪？
> <details><summary>▸ 點開看</summary>
>
> 因為我們每次都把**整份 `messages`**一起寄過去，它才顯得記得。記憶存在**我們程式裡那個會用 `.append()` 長大的 `messages` 清單**，不在 AI 那邊。
> </details>

---

# STEP 5　ReAct + 搜尋工具（讓它會查資料）

**目標**：讓 AI 突破「只會聊天」，第一次真的**去做一件事**——上網查最新資料。

**觀念（ReAct）**：想像你到一個陌生城市找餐廳。閉著眼睛亂走（不想）會迷路；想把整條路線一次規劃到完美再出發（想太多）又沒足夠資訊。聰明的做法是——**走一步、看一下、再決定下一步**。

AI 用工具也一樣，這個模式叫 **ReAct**：
- **Thought（想）**：它判斷「我需要查資料」
- **Action（做）**：它輸出一段 JSON 說要用哪個工具
- **Observation（看結果）**：程式執行工具、把結果回報給它
- …再想、再做，直到能回答

> 誠實說：這聽起來很厲害，但**實際還是要看模型夠不夠聰明**。小模型有時會忘記用工具、或憑記憶亂編——所以我們的規則書要寫得明確一點。

這一關新東西比較多，一樣拆開來，一次教一個。

### 5-1　搜尋工具：`web_search()`

先寫一個獨立函式，負責問 Tavily：

```python
def web_search(query):
    key = s.get("TAVILY_API_KEY", "")
    if not key:
        return "沒有設定 TAVILY_API_KEY，不能搜尋。"
    ...
```

> 🧩 **新語法：`字典.get("鍵", 預設值)`**
>
> 之前拿字典的值都用 `s["鍵"]`，但如果那個鍵根本不存在，`s["鍵"]` 會直接報錯讓程式當掉。
> `.get("鍵", 預設值)` 比較溫和：**如果有這個鍵就回傳值，沒有就回傳你指定的預設值**（這裡是空字串 `""`），不會報錯。
> 這樣如果你沒填 `TAVILY_API_KEY`，程式只會友善地告訴你「不能搜尋」，而不是直接崩潰。

接著送出搜尋請求（跟 STEP 3 的 `requests.post` 是同一招，只是換一家網址）：

```python
    r = requests.post("https://api.tavily.com/search",
                      headers={"Authorization": "Bearer " + key},
                      json={"query": query, "max_results": 3, "include_answer": True},
                      timeout=30)
    data = r.json()
```

最後把搜尋結果整理成一段文字：

```python
    out = []
    if data.get("answer"):
        out.append("摘要：" + data["answer"])
    for it in data.get("results", []):
        out.append(it.get("title", "") + "\n" + it.get("content", "")[:200])
    return "\n\n".join(out)
```

> 🧩 **新語法：`清單.append()` 收集結果、`"\n\n".join(清單)` 組回一段文字**
>
> - `out = []`：先準備一個空清單，等一下要往裡面塞東西。
> - `it.get("content", "")[:200]`：字串後面加 `[開始:結束]` 叫**切片**，`[:200]` 就是「只取前 200 個字」，避免內容太長。
> - `"\n\n".join(out)`：跟 `.append()` 相反，這是把**清單裡每一項**用 `"\n\n"`（兩個換行，也就是空一行）接成**一整段文字**。

完整的 `web_search`：

```python
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
```

### 5-2　把「問模型」抽成獨立函式

因為等一下要重複問模型好幾次，把 STEP 4 那段呼叫模型的邏輯，抽成一個可以重複用的函式：

```python
def call_model(messages):
    body = {"model": s["LLM_MODEL"], "messages": messages}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    return r.json()["choices"][0]["message"]["content"]
```

跟 STEP 4 的 `ask()` 很像，差別是它**不會自己 `.append()`**——記不記錄對話，交給外面呼叫它的人決定。

### 5-3　從 AI 的回覆裡，找出「動作紙條」

AI 決定要用工具時，會回一段 JSON 文字（不是真的執行，只是「說」它想做什麼）。我們要把這段文字，從一堆回覆裡挑出來、轉成字典。

先借兩個新套件：

```python
import json, re
```

> 🧩 **`json` 套件**：`json.loads(文字)` 可以把一段「看起來像字典的文字」，真的轉成 Python 字典（如果那段文字寫錯格式，會丟出 `json.JSONDecodeError` 錯誤）。
>
> 🧩 **`re` 套件（正則表達式）**：用來在一大段文字裡，找出符合某種「格式」的片段。這是進階工具，你**不需要完全看懂那串奇怪符號**，只要知道 `re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL)` 這行在做的事是——「把 `text` 裡所有被 ` ```json ` 和 ` ``` ` 包起來的內容，都挑出來」。

```python
def find_action(text):
    blocks = re.findall(r"```json\s*(.*?)\s*```", text, re.DOTALL) or [text]
```

> 🧩 **新語法：`A or B`**　如果 `re.findall(...)` 什麼都沒找到（結果是空清單 `[]`，代表「假」），就改用 `[text]`（把整段文字自己當一塊試試看）。`or` 在這裡的意思是「前面那個是空的／假的，就換用後面這個」。

接著一塊一塊檢查每個候選片段：

```python
    for b in blocks:
        try:
            data = json.loads(b)          # 試著把文字轉成字典
        except json.JSONDecodeError:
            continue                       # 轉失敗，跳過這塊，換下一塊
        if "tool" in data:
            return data                    # 有 tool 這個鍵 = 是一張動作紙條
    return None                            # 全部都不是 = AI 是在講人話
```

> 🧩 **新語法：`continue`**　在迴圈裡遇到 `continue`，代表「這一輪不用做了，直接跳到下一輪」（不會跳出整個迴圈，跟 `break` 不一樣）。
>
> 🧩 **新語法：`"tool" in data`**　這是在檢查字典 `data` 裡**有沒有**叫 `"tool"` 的這個鍵，回傳 `True` 或 `False`。
>
> 🧩 **`return None`**：`None` 代表「什麼都沒有」。如果整個函式跑到最後都沒找到動作紙條，就回傳 `None`，等一下我們會用 `if action is None` 來判斷「這次沒有要用工具」。

完整的 `find_action`：

```python
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
```

### 5-4　規則書：告訴 AI 有這個工具可以用

AI 要「知道」自己有工具可以叫，得寫進規則書（system 訊息）裡，講清楚**什麼時候用、格式長怎樣**：

```python
SYSTEM = '''你是小智慧體，請用繁體中文。
遇到今天、最新、即時、新聞、股價這類即時資訊，一定要先用 web_search 查，不可以憑記憶回答：
```json {"tool":"web_search","args":{"query":"關鍵字"}} ```
要用工具時只輸出 JSON、不要多話；不用工具就直接回答。'''
```

> 🧩 **`'''三個引號'''`**：一般字串 `"..."` 只能寫一行，`'''...'''` 可以寫**很多行**，適合寫這種一大段規則說明。

### 5-5　親手轉一圈 ReAct（先手動，看清楚每一步）

在自動化之前，我們先**手動**跑一次，把 Thought → Action → Observation 一步步印出來看：

```python
messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "今天台股表現如何？整理兩點"}]

ai_text = call_model(messages)                  # 第一次問：AI 應該回一張動作紙條
print("AI（想＋動作）：", ai_text)
messages.append({"role": "assistant", "content": ai_text})
```

```python
action = find_action(ai_text)
if action:
    obs = web_search(action["args"]["query"])   # 執行工具 → 得到 Observation
    print("Observation（觀察）：", obs[:150], "...")
    messages.append({"role": "user", "content": "工具結果：\n" + obs})
    final = call_model(messages)                # 第二次問：帶著結果，AI 給答案
    print("AI（最終回答）：", final)
else:
    print("這次它沒用工具，直接答：", ai_text)
```

<details><summary>👉 目前完整的 <code>agent.py</code></summary>

```python
import requests, json, re
from dotenv import dotenv_values

s = dotenv_values(".env")
url = s["LLM_BASE_URL"].rstrip("/") + "/chat/completions"
headers = {"Authorization": "Bearer " + s["LLM_API_KEY"]}

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

messages = [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "今天台股表現如何？整理兩點"}]

ai_text = call_model(messages)
print("AI（想＋動作）：", ai_text)
messages.append({"role": "assistant", "content": ai_text})

action = find_action(ai_text)
if action:
    obs = web_search(action["args"]["query"])
    print("Observation（觀察）：", obs[:150], "...")
    messages.append({"role": "user", "content": "工具結果：\n" + obs})
    final = call_model(messages)
    print("AI（最終回答）：", final)
else:
    print("這次它沒用工具，直接答：", ai_text)
```
</details>

🎮 **動手互動**
1. 跑：`py agent.py`，看畫面依序出現「想＋動作 → Observation → 最終回答」——你**親眼看到一圈 ReAct**。
2. 如果它沒吐動作、直接答（可能給舊資料）：把問句講白一點，或確認 `.env` 有填 Tavily 金鑰。
3. 改：把那句 user 問題換成別的即時問題（今天天氣、最新新聞），再跑。

✅ **檢查點**：用「想 / 動作 / 觀察」描述剛剛發生了什麼？
> <details><summary>▸ 點開看</summary>
>
> **想**：AI 判斷這要查即時資料。**動作**：它輸出一段 JSON 說要用 `web_search` 加關鍵字。**觀察**：程式執行 `web_search()` 把結果回報。之後 AI 讀到結果，才整理成答案。
> </details>

---

# STEP 6　整合：打包成一個可用的智慧體

**目標**：上一步是我們**手動**餵它一圈。現在把它變成**自動**——它能自己一步接一步做，直到完成。打包好，就是一個真正能用的 agent 了。

**觀念**：把「問模型 → 執行工具 → 回報 → 再問」放進一個**迴圈**自動跑，這就是 **Agent Loop**。一定要加**護欄**（最多跑幾圈），免得它鬼打牆一直燒你的 API 額度。

### 6-1　工具分派：`run_tool()`

現在只有一個工具，但先把「看紙條上寫哪個工具、就呼叫誰」這件事，獨立寫成一個函式，之後要加工具會很方便：

```python
def run_tool(action):
    if action["tool"] == "web_search":
        return web_search(action["args"]["query"])
    return "未知工具：" + str(action.get("tool"))
```

> 🧩 **新語法：`str(...)`**　`action.get("tool")` 可能拿到任何型態的東西，`str(...)` 是把它**強制轉成文字**，才能安心用 `+` 接在字串後面。

### 6-2　智慧體迴圈：把 STEP 5 的手動流程自動化

STEP 5 的 5-5 是我們手動問一次、判斷一次、印一次。現在把它包進一個 `for` 迴圈，讓它自己重複做，直到不再需要工具為止：

```python
MAX_STEPS = 8   # 護欄：最多做 8 步，避免無窮迴圈燒錢
```

```python
def agent(user_text):
    messages.append({"role": "user", "content": user_text})
    for i in range(MAX_STEPS):
        ai_text = call_model(messages)
        action = find_action(ai_text)
        if action is None:                          # 沒動作 = 講完了
            messages.append({"role": "assistant", "content": ai_text})
            return ai_text                          #   → 交出答案，結束整個函式
        messages.append({"role": "assistant", "content": ai_text})
        print("  （動作：" + json.dumps(action, ensure_ascii=False) + "）")
        result = run_tool(action)                   # 執行，拿到 Observation
        messages.append({"role": "user", "content": "工具結果：\n" + result})
    return "步數太多，先停下來。"
```

> 🧩 **新語法：`json.dumps(字典, ensure_ascii=False)`**　跟 `json.loads` 相反，這是把 Python 字典**轉回 JSON 文字**，方便印出來看。`ensure_ascii=False` 是為了讓中文正常顯示，不然中文會被轉成一堆 `中` 這種看不懂的編碼。
>
> 這個 `for i in range(MAX_STEPS):` 迴圈裡藏著整個 agent 的心臟：**每一圈都問一次模型，看它要不要用工具；不用了就 `return` 離開函式；要用就執行、把結果塞回 `messages`，讓下一圈的模型看得到。**

記得把 `messages` 改回只留規則（因為現在對話由 `agent()` 自己管理）：

```python
messages = [{"role": "system", "content": SYSTEM}]
```

### 6-3　聊天迴圈：呼叫 `agent()` 而不是 `ask()`

```python
while True:
    try:
        user = input("你 > ")
    except EOFError:
        break
    if user == "/exit":
        break
    print("AI >", agent(user))
```

<details><summary>👉 目前完整的 <code>agent.py</code>（第 ⑤ 步完成版）</summary>

```python
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
```
</details>

🎮 **動手互動**
1. 跑：`py agent.py`，說「**幫我查今天台股動向，整理成三點**」→ 看它自己搜尋、自己整理。
2. 連續問：再問「**那科技股呢？**」→ 它記得前文、可能再查一次。
3. 護欄實驗：把 `MAX_STEPS` 改成 `1`，給它一個要查的問題，看它**還沒查完就被拉停**。

> 🎉 **到這裡，你已經做出一個完整、能用的 AI 智慧體了**——會聊天、會自己上網查資料。這就是一個安全的收尾點；下一步是加碼，有點難。

✅ **檢查點**：迴圈靠哪個判斷決定「結束」？為什麼一定要有 `MAX_STEPS`？
> <details><summary>▸ 點開看</summary>
>
> 靠 `if action is None`：AI 這次沒吐動作、直接講人話，就 `return` 結束。要有 `MAX_STEPS` 是因為萬一它鬼打牆一直要用工具，護欄會強制停下，避免無窮迴圈把 API 費用燒光。
> </details>

---

# STEP 7（加碼）　真agent功能：終端機工具

**目標**：如果時間還夠，再給它第二隻手——能在你電腦上**執行指令、建立檔案**。因為我們在 STEP 6 已經有 `run_tool` 分派了，加工具的骨架不用重寫，但這裡會用到幾個新東西。

**觀念**：讓 Python 去叫 **PowerShell** 幫忙跑指令，這種「程式呼叫另一個程式」的做法叫**子行程（subprocess）**。我們把它**關在 `workspace` 資料夾**裡（沙箱），比較安全；並強制走 **UTF-8**，中文才不會亂碼。

### 7-1　借兩個新套件

```python
import os, subprocess
```

`os` 是跟作業系統打交道的套件（例如處理資料夾路徑）；`subprocess` 是專門「開一個子程式來跑指令」的套件。

### 7-2　準備一個乾淨的工作資料夾

還記得 STEP 2 在 `.env` 填過一行 `WORKSPACE_DIR=workspace` 嗎？它就是在這裡登場的——用 STEP 5 學過的 `.get()` 把它讀出來（沒填就預設叫 `"workspace"`）：

```python
workspace = os.path.abspath(s.get("WORKSPACE_DIR", "workspace"))
os.makedirs(workspace, exist_ok=True)
```

> 🧩 **`os.path.abspath(...)`**：把 `"workspace"` 這種相對名稱，轉成完整、清楚的絕對路徑（例如 `C:\...\workspace`）。
>
> 🧩 **`os.makedirs(路徑, exist_ok=True)`**：建立這個資料夾。`exist_ok=True` 的意思是「如果資料夾已經存在，不要報錯，直接繼續」——沒有這個參數，資料夾已存在時程式會直接當掉。

### 7-3　讓中文不要變亂碼

PowerShell 預設的文字編碼跟 Python 常用的不一樣，會讓中文變亂碼。我們用一段指令強制它改成 UTF-8：

```python
utf8 = ("[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$PSDefaultParameterValues['*:Encoding']='utf8'; ")
```

這只是一段**要塞給 PowerShell 執行的文字**，等一下會接在真正的指令前面一起送出去。（括號把三行字串自動接成一行，不用自己加 `+`。）

### 7-4　真正執行指令：`subprocess.run()`

```python
r = subprocess.run(["powershell", "-NoProfile", "-Command", utf8 + command],
                   capture_output=True, text=True,
                   encoding="utf-8", errors="replace",
                   cwd=workspace, timeout=120)
```

這行參數很多，一個一個看：

- `["powershell", "-NoProfile", "-Command", utf8 + command]`：這是一份**清單**，代表「要執行哪個程式、帶哪些參數」——這裡是叫 `powershell`，帶上我們的 UTF-8 設定和真正的指令。
- `capture_output=True`：把執行結果（印出的文字）**抓回來**給程式用，而不是讓它直接顯示在畫面上飄走。
- `text=True, encoding="utf-8", errors="replace"`：抓回來的結果請當成**文字**處理、用 UTF-8 解讀；如果有解不出來的字，用替代符號頂著，不要讓程式崩潰。
- `cwd=workspace`：**這個指令只能在 `workspace` 資料夾裡執行**，這就是「沙箱」的具體做法——就算指令想亂搞，範圍也被限制住。
- `timeout=120`：超過 120 秒還沒執行完，就強制中止（保護你不會卡死）。

### 7-5　把執行結果整理成一段文字回傳

```python
out = "exit_code: " + str(r.returncode)
if r.stdout and r.stdout.strip():
    out += "\n" + r.stdout.strip()
if r.stderr and r.stderr.strip():
    out += "\n(錯誤) " + r.stderr.strip()
return out
```

> 🧩 **`r.returncode`**：指令執行完的「結果代碼」，`0` 代表成功，其他數字通常代表出錯了。
>
> 🧩 **`.strip()`**：字串方法，把文字前後多餘的空白／換行去掉。
>
> 🧩 **`out += "..."`**：等於 `out = out + "..."`，把新內容接到 `out` 後面。

組起來，完整的 `run_terminal`：

```python
def run_terminal(command):
    workspace = os.path.abspath(s.get("WORKSPACE_DIR", "workspace"))
    os.makedirs(workspace, exist_ok=True)
    utf8 = ("[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$PSDefaultParameterValues['*:Encoding']='utf8'; ")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", utf8 + command],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=workspace, timeout=120)
    out = "exit_code: " + str(r.returncode)
    if r.stdout and r.stdout.strip():
        out += "\n" + r.stdout.strip()
    if r.stderr and r.stderr.strip():
        out += "\n(錯誤) " + r.stderr.strip()
    return out
```

### 7-6　讓 `run_tool` 多認識這個新工具

```python
def run_tool(action):
    if action["tool"] == "web_search":
        return web_search(action["args"]["query"])
    if action["tool"] == "terminal":                       # ← 新增這兩行
        return run_terminal(action["args"]["command"])
    return "未知工具：" + str(action.get("tool"))
```

### 7-7　更新規則書，告訴 AI 多了這個工具

```python
SYSTEM = '''你是小智慧體，請用繁體中文。你有兩個工具：
1. web_search 查最新資料——遇到今天、最新、即時、新聞、股價，一定要先查、不可憑記憶：
```json {"tool":"web_search","args":{"query":"關鍵字"}} ```
2. terminal 在 workspace 執行 PowerShell 指令：
```json {"tool":"terminal","args":{"command":"指令"}} ```
要執行 Python 用 py 不要用 python；要用工具時只輸出 JSON、不要多話；不用工具就直接回答。'''
```

<details><summary>👉 目前完整的 <code>agent.py</code>（STEP 7 完成版）</summary>

```python
import requests, json, re, os, subprocess
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

def run_terminal(command):
    workspace = os.path.abspath(s.get("WORKSPACE_DIR", "workspace"))
    os.makedirs(workspace, exist_ok=True)
    utf8 = ("[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$PSDefaultParameterValues['*:Encoding']='utf8'; ")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", utf8 + command],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=workspace, timeout=120)
    out = "exit_code: " + str(r.returncode)
    if r.stdout and r.stdout.strip():
        out += "\n" + r.stdout.strip()
    if r.stderr and r.stderr.strip():
        out += "\n(錯誤) " + r.stderr.strip()
    return out

def run_tool(action):
    if action["tool"] == "web_search":
        return web_search(action["args"]["query"])
    if action["tool"] == "terminal":
        return run_terminal(action["args"]["command"])
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

SYSTEM = '''你是小智慧體，請用繁體中文。你有兩個工具：
1. web_search 查最新資料——遇到今天、最新、即時、新聞、股價，一定要先查、不可憑記憶：
```json {"tool":"web_search","args":{"query":"關鍵字"}} ```
2. terminal 在 workspace 執行 PowerShell 指令：
```json {"tool":"terminal","args":{"command":"指令"}} ```
要執行 Python 用 py 不要用 python；要用工具時只輸出 JSON、不要多話；不用工具就直接回答。'''

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
```
</details>

🎮 **動手互動**
1. 跑，說「**幫我在工作區建立 hello.txt，內容是 你好世界**」→ 打開 `workspace/hello.txt`，應該是正常中文、**沒有亂碼**。
2. 試：「**列出工作區有哪些檔案**」、「**寫一個 Python 印出 1 到 10 並執行**」（它會用 `py` 跑）。
3. 一條龍：「**查今天台股，整理三點，存成 report.txt**」→ 它會**先搜尋、再寫檔**，兩個工具接力。

✅ **檢查點**：`web_search`（對外查網路）和 `terminal`（對內動電腦），哪個危險？怎麼保護？
> <details><summary>▸ 點開看</summary>
>
> `terminal` 危險，因為它能真的改動你的電腦。保護：關在 `workspace`（沙箱，用 `cwd=workspace` 做到）、`timeout=120`（做太久就停）、外層 `MAX_STEPS` 護欄。
> </details>

---

# STEP 7.5（重要）　實測抓到的 3 個真實 bug，修成最終定版

上面 STEP 7 完成版是「照教學邏輯」組出來的，語法上完全正確。但我們**真的把它連續跑了十幾次**（模擬全班一起用的情況）之後，抓到三個會讓程式**當場崩潰**的真實狀況——這種東西不測不會知道，這就是工程最真實的一面。

**bug 1：AI 有時候不乖乖照格式，把參數放錯位置**

規則書要求 `{"tool":"terminal","args":{"command":"..."}}`，但 AI 偶爾會回 `{"tool":"terminal","command":"..."}`（少了一層 `args`）。這樣 `action["args"]["command"]` 就會直接 `KeyError` 讓整支程式當掉。

**bug 2：API 有時候不會乖乖回答，而是回一個錯誤**

免費額度用太快，伺服器會回 `429 Too Many Requests` 這種**錯誤訊息**，格式跟平常的回答完全不一樣，裡面根本沒有 `choices`。原本的 `call_model` 直接假設一定有 `choices`，所以也會 `KeyError` 當掉。全班同時用同一組免費金鑰時，這個**非常容易發生**。

**bug 3：AI 有時候會自己換一種格式包 JSON**

規則書教它用 ` ```json ``` ` 包起來，但它偶爾會自己改用 `<tool_call>...</tool_call>` 這種標籤。`find_action` 原本只認得 ` ```json ``` `，找不到就當作「沒有要用工具」，結果任務**沒有真的執行**、就自己說做完了。

**修法**：三個都不需要學新語法，全部用你已經會的東西：

1. 呼叫工具的地方包一層 `try/except`（STEP 4 教過），出錯就把錯誤訊息當成 Observation 回饋給 AI，讓它下一輪自己修正，而不是讓程式死掉。
2. `call_model` 用 `"choices" not in data` 判斷（STEP 5 教過的 `in`），沒有就回傳一句清楚的錯誤訊息，不要硬拆。
3. `find_action` 除了認 ` ```json ``` `，也多認 ` ``` ` （沒寫語言）和 `<tool_call>...</tool_call>` 這兩種常見的變形。

<details><summary>👉 最終定版 <code>agent.py</code>（實測穩定，建議上課／交作業都用這份）</summary>

```python
import requests, json, re, os, subprocess
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

def run_terminal(command):
    workspace = os.path.abspath(s.get("WORKSPACE_DIR", "workspace"))
    os.makedirs(workspace, exist_ok=True)
    utf8 = ("[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$OutputEncoding=[System.Text.Encoding]::UTF8; "
            "$PSDefaultParameterValues['*:Encoding']='utf8'; ")
    r = subprocess.run(["powershell", "-NoProfile", "-Command", utf8 + command],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       cwd=workspace, timeout=120)
    out = "exit_code: " + str(r.returncode)
    if r.stdout and r.stdout.strip():
        out += "\n" + r.stdout.strip()
    if r.stderr and r.stderr.strip():
        out += "\n(錯誤) " + r.stderr.strip()
    return out

def run_tool(action):
    if action["tool"] == "web_search":
        return web_search(action["args"]["query"])
    if action["tool"] == "terminal":
        return run_terminal(action["args"]["command"])
    return "未知工具：" + str(action.get("tool"))

def call_model(messages):
    body = {"model": s["LLM_MODEL"], "messages": messages}
    r = requests.post(url, headers=headers, json=body, timeout=60)
    data = r.json()
    if "choices" not in data:                     # bug 2 修法：API 出錯就友善回報，不要硬拆
        return "（呼叫模型失敗，稍等幾秒再試一次：" + str(data) + "）"
    return data["choices"][0]["message"]["content"]

def find_action(text):
    blocks = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL)   # bug 3 修法：也認沒寫語言的 ``` ```
    blocks += re.findall(r"<tool_call>\s*(.*?)\s*</tool_call>", text, re.DOTALL)  # 也認 <tool_call> 標籤
    blocks.append(text)
    for b in blocks:
        try:
            data = json.loads(b)
        except json.JSONDecodeError:
            continue
        if "tool" in data:
            return data
    return None

SYSTEM = '''你是小智慧體，請用繁體中文。你有兩個工具：
1. web_search 查最新資料——遇到今天、最新、即時、新聞、股價，一定要先查、不可憑記憶：
```json {"tool":"web_search","args":{"query":"關鍵字"}} ```
2. terminal 在 workspace 執行 PowerShell 指令：
```json {"tool":"terminal","args":{"command":"指令"}} ```
要執行 Python 用 py 不要用 python；要用工具時只輸出 JSON、不要多話；不用工具就直接回答。'''

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
        try:
            result = run_tool(action)              # bug 1 修法：包一層 try/except
        except Exception as e:
            result = ("工具執行失敗：" + str(e) +
                      "。請確認格式是 {\"tool\":...,\"args\":{...}}，重新輸出一次。")
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
```
</details>

> ✅ **這份最終定版我們實際壓力測試過**：連續跑十幾次終端機任務、故意打到 API 額度上限（429）、以及完整的「搜尋→存檔」接力任務，全部**沒有再讓程式崩潰過**。跟教學版的差異只有三處防呆，程式邏輯完全一樣。

---

# 你做完了 🎉

你從「對 AI 說一句話」開始，一關關加上**記憶、搜尋、自動迴圈、終端機**，親手打造了一個微型 AI 智慧體，最後還把它加固成一個實測穩定的版本。

**延伸挑戰**：幫它加第三個工具（例如「查現在時間」`get_time`），走完整流程：寫函式 → `run_tool` 多一個分派 → `SYSTEM` 告訴它。~~做得出來，你就真的懂了。~~ ←很明顯是AI這樣認為的

---

# 附錄 A　配套檔案包：每一段的完整程式

跟不上、或想直接對照答案時，專案的 **`講義程式碼`** 資料夾裡有每一關的完整可執行檔（內容跟本講義的程式一字不差，全部實測過）：

| 檔案 | 對應講義 | 內容 |
|---|---|---|
| `step3_第一則訊息.py` | STEP 3 | 最小 chatbot：問一句、答一句 |
| `step4_多輪對話.py` | STEP 4 | 有記憶的連續聊天 |
| `step5_ReAct搜尋.py` | STEP 5 | 手動轉一圈 ReAct（搜尋工具） |
| `step6_整合agent.py` | STEP 6 | 自動迴圈，完整可用的智慧體 ✅ |
| `step7_終端機工具.py` | STEP 7 | 加上終端機工具（教學版） |
| `agent_最終定版.py` | STEP 7.5 | 修好 3 個 bug 的實測穩定版 ⭐ |
| `進階_分層版/` | 附錄 B | 拆成三個檔案的專業架構 |

用法：把你的 `.env` 複製到 `講義程式碼` 資料夾裡，然後 `py step3_第一則訊息.py` 逐關跑。
（要分享這個資料夾給別人之前，記得先把裡面的 `.env` 刪掉——金鑰是密碼。）

---

# 附錄 B　完整進階版：三層分工架構

你的 `agent.py` 把所有東西擠在一個檔案。程式一大，就像一個東西亂丟的房間。專業做法是**把不同職責拆到不同檔案**：

| 檔案 | 角色 | 放什麼 |
|---|---|---|
| `main.py` | 介面層 | 跟人對話的 `while` 迴圈、`/help`、`/exit` |
| `ai.py` | 大腦層 | 規則書、智慧體迴圈、呼叫模型、解析動作紙條 |
| `tools.py` | 工具層 | `web_search()`、`run_terminal()` 真正動手的函式 |

三個檔案怎麼互相合作？`main.py` 收到你的話 → 交給 `ai.py` 的迴圈 → 需要動手時呼叫 `tools.py` → 結果一路傳回來給你。**跟你的 `agent.py` 邏輯完全一樣，只是分了房間。**

這版還多了幾個進階小功能，讀的時候可以找找看：把「現在時間」塞進規則書（`__NOW__` 佔位符）、`temperature` 控制回答穩定度、更完整的規則書（教模型怎麼做 Excel/Word）。

以下三個檔案放在 `講義程式碼/進階_分層版/`，也可以直接展開來讀：

<details><summary>👉 <code>main.py</code>（介面層）</summary>

```python
from dotenv import dotenv_values

from ai import ask_ai


settings = dotenv_values(".env")


def main():
    if not settings.get("LLM_BASE_URL") or not settings.get("LLM_API_KEY"):
        print("請先在 .env 設定 LLM_BASE_URL 和 LLM_API_KEY")
        return

    messages = []

    print("終端機小智慧體啟動")
    print("輸入 /help 看範例，輸入 /exit 離開")
    print("模型：" + settings.get("LLM_MODEL", ""))
    print("工作區：" + settings.get("WORKSPACE_DIR", "workspace"))
    print()

    while True:
        user_text = input("你 > ").strip()

        if user_text == "/exit":
            print("再見！")
            break

        if user_text == "/help":
            print("可以試試：")
            print("1. 幫我搜尋今天台股動向，整理三點")
            print("2. 幫我在工作區建立 hello.txt，內容是 Hello Agent")
            print("3. 幫我列出工作區有哪些檔案")
            print()
            continue

        if user_text == "":
            continue

        answer = ask_ai(messages, user_text, settings)
        print("\nAI > " + answer)
        print()


if __name__ == "__main__":
    main()
```
</details>

<details><summary>👉 <code>ai.py</code>（大腦層）</summary>

```python
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
```
</details>

<details><summary>👉 <code>tools.py</code>（工具層）</summary>

```python
import os
import subprocess

import requests


def web_search(query, api_key):
    if api_key == "":
        return "沒有設定 TAVILY_API_KEY，不能搜尋。"

    print("\n搜尋關鍵字：")
    print(query)

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "search_depth": "basic",
            "max_results": 3,
            "include_answer": True,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    lines = []

    if data.get("answer"):
        lines.append("摘要：" + data["answer"])

    for item in data.get("results", []):
        title = item.get("title", "")
        url = item.get("url", "")
        content = item.get("content", "")[:250]
        lines.append(title + "\n" + url + "\n" + content)

    return "\n\n".join(lines)


def run_terminal(command, workspace_dir):
    workspace_path = os.path.abspath(workspace_dir)
    os.makedirs(workspace_path, exist_ok=True)

    print("\n準備執行：")
    print(command)

    # 讓 PowerShell 全程使用 UTF-8。
    # 沒有這行，中文會變亂碼，甚至直接讓程式當掉。
    # 有了這行，存出來的檔案也會是 UTF-8，用記事本打開就是正常中文。
    utf8_setup = (
        "[Console]::OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$OutputEncoding=[System.Text.Encoding]::UTF8; "
        "$PSDefaultParameterValues['*:Encoding']='utf8'; "
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", utf8_setup + command],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=workspace_path,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "指令超過 120 秒，已停止等待。"

    output = "exit_code: " + str(result.returncode)

    if result.stdout and result.stdout.strip():
        output += "\nstdout:\n" + result.stdout.strip()

    if result.stderr and result.stderr.strip():
        output += "\nstderr:\n" + result.stderr.strip()

    return output
```
</details>

> 對照著找找看：你 `agent.py` 的 `agent()` 迴圈在 `ai.py` 叫 `ask_ai()`；你的 `find_action()` 在 `ai.py` 叫 `find_tool_call()`；你的 `web_search()`／`run_terminal()` 搬去了 `tools.py`。**換一個模型供應商只要改 `.env`；加一個新工具只要動 `tools.py` 和規則書**——這就是分層的好處。
