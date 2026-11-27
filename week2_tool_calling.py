import json
import os
import urllib.request
from openai import OpenAI

client = OpenAI(
    base_url=os.getenv("OPENAI_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    api_key=os.getenv("OPENAI_API_KEY", ""),
)
MODEL = os.getenv("OPENAI_MODEL", "moonshotai/kimi-k2-instruct")

# 1. 定義 tool schema
tools = [
    {
        "type": "function",
        "function": {
            "name": "http_get",
            "description": "Fetch a URL with HTTP GET. Return status code and a short body summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Absolute http(s) URL to fetch.",
                    }
                },
                "required": ["url"],
            },
        },
    }
]


# 2. 本地端實際執行的函式
def http_get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Week2-ToolCaller/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        status = resp.status
        text = resp.read().decode("utf-8", errors="replace")
    summary = " ".join(text.split())[:200]
    return json.dumps({"status": status, "summary": summary}, ensure_ascii=False)


messages = [
    {
        "role": "user",
        "content": "請幫我用 http_get 抓 https://example.com 的內容，並簡述回傳結果。",
    }
]

# === 第一筆 API 交易：送出 tools，取得模型提出的 tool_calls ===
resp1 = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
    tool_choice="auto",
)

msg1 = resp1.choices[0].message
tool_calls = msg1.tool_calls or []

print("=== [第 1 筆回應] 模型提出 tool_calls ===")
for tc in tool_calls:
    print(f"id: {tc.id}")
    print(f"name: {tc.function.name}")
    print(f"arguments (raw string): {tc.function.arguments}")

# 重要：先把 assistant 這則包含 tool_calls 的訊息放進對話歷史
messages.append(msg1.model_dump())

# === 程式端實際執行工具，並組裝 role: "tool" 訊息 ===
print("\n=== [程式執行] 本地端執行 http_get 並準備回填 ===")
for tc in tool_calls:
    if tc.function.name == "http_get":
        # arguments 是 JSON 字串，必須先 json.loads 解析
        args = json.loads(tc.function.arguments)
        result_str = http_get(args["url"])
        print(f"執行結果 ({tc.id}): {result_str}")

        tool_msg = {
            "role": "tool",
            "tool_call_id": tc.id,
            "content": result_str,
        }
        messages.append(tool_msg)

print("\n=== [第 2 筆請求] 回填的 role='tool' 訊息 ===")
for m in messages:
    if m.get("role") == "tool":
        print(json.dumps(m, ensure_ascii=False, indent=2))

# === 第二筆 API 交易：帶著 tool 結果請模型生成最終回覆 ===
resp2 = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
)

print("\n=== [第 2 筆回應] 模型最終回覆 ===")
print(resp2.choices[0].message.content)
