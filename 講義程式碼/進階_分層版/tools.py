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
