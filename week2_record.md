# Week 2：工具描述與分派觀察紀錄

## 完整執行輸出

```text
status: 200
tool_calls: [
  {
    "id": "call-d697e06a-54da-4783-b3e8-41813eb6aafe",
    "type": "function",
    "function": {
      "name": "http_get",
      "arguments": "{\\"url\\":\\"https://example.com\\"}"
    }
  }
]
模型建議: {"url":"https://example.com"}
程式執行: {"status_code": 200, "body_summary": "<!doctype html><html lang=en><head><meta charset=utf-8><link rel=icon href=data:,><meta name=viewport content=\"width=dev"}
status: 200
reply: 抓取成功（HTTP 200），我看到的是 example.com 的標準示範頁面，包含一個標題為「Example Domain」的巨大標題，以及一段說明此頁面可供網頁設計者參考的文字和一個指向 IANA 的「More information...」連結。
```

## 兩次呼叫重點整理

| 步驟 | 模型建議 | 程式實際執行 |
| :--- | :--- | :--- |
| **第一次 API 回應** | `name`: `http_get`，`arguments`: `{"url":"[https://example.com](https://example.com)"}`（`id`: `call-d697e06a-54da-4783-b3e8-41813eb6aafe`） | 尚未執行；僅接收並解析模型建議的參數 |
| **工具執行** | 無 | 呼叫 `requests.get`，取得 `status_code: 200` 與前 120 字元 `body_summary`（`<!doctype html><html lang=en><head><meta charset=utf-8><link rel=icon href=data:,><meta name=viewport content="width=dev`） |
| **第二次 API 請求** | 無 | 回填 `role: "tool"` 訊息，且 `tool_call_id` 設為 `call-d697e06a-54da-4783-b3e8-41813eb6aafe` |
| **第二次 API 回應** | 無 | 取得最終回答（`choices[0].message.content`）：抓取成功（HTTP 200），看到 example.com 標準示範頁面 |
