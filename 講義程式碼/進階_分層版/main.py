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
