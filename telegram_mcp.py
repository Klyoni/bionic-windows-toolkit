import sys
import json
import asyncio
import os
from telethon import TelegramClient, connection

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

API_ID = int(os.environ.get("TG_API_ID", "6"))
API_HASH = os.environ.get("TG_API_HASH", "eb06d4abfb49dc3eeb1aeb98ae0f581e")
SESSION_PATH = os.path.join(os.path.expanduser("~"), ".lmstudio", "bionic_tg_session")

TG_PROXY_TYPE = os.environ.get("TG_PROXY_TYPE", "mtproto")
TG_PROXY_HOST = os.environ.get("TG_PROXY_HOST", "127.0.0.1")
TG_PROXY_PORT = int(os.environ.get("TG_PROXY_PORT", 1080))
TG_PROXY_SECRET = os.environ.get("TG_PROXY_SECRET", "")

TOOLS = [
    {
        "name": "get_unread_messages",
        "description": "Читает непрочитанные сообщения из диалогов, групп и каналов Telegram, не отмечая их прочитанными.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit_chats": {"type": "integer", "default": 15},
                "messages_per_chat": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "list_dialogs",
        "description": "Показывает список чатов, групп и каналов пользователя (фильтруя по части названия query, если указано) с их точными названиями, @username и числовыми ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "default": ""},
                "limit": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "read_chat_messages",
        "description": "Читает последние сообщения из чата, группы или канала по точному названию, @username или числовому ID (chat_query).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "chat_query": {"type": "string"},
                "limit": {"type": "integer", "default": 15},
                "search_text": {"type": "string", "default": ""},
            },
            "required": ["chat_query"],
        },
    },
    {
        "name": "search_global_messages",
        "description": "Ищет сообщения по ключевому слову. Параметр chat_type ограничивает поиск: 'all' (везде), 'private' (только личные чаты), 'group' (только группы), 'channel' (только каналы).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 15},
                "chat_type": {
                    "type": "string",
                    "enum": ["all", "private", "group", "channel"],
                    "default": "all",
                },
            },
            "required": ["query"],
        },
    },
]

def get_client() -> TelegramClient:
    proxy = None
    conn = None
    
    if TG_PROXY_TYPE:
        if TG_PROXY_TYPE == "mtproto":
            conn = connection.ConnectionTcpMTProxyRandomizedIntermediate
            proxy = (TG_PROXY_HOST, TG_PROXY_PORT, TG_PROXY_SECRET)
        elif TG_PROXY_TYPE == "socks5":
            proxy = (TG_PROXY_HOST, TG_PROXY_PORT)
        elif TG_PROXY_TYPE == "http":
            proxy = (TG_PROXY_HOST, TG_PROXY_PORT)
    
    return TelegramClient(
        SESSION_PATH,
        API_ID,
        API_HASH,
        connection=conn,
        proxy=proxy,
    )

async def run_tool(name: str, args: dict) -> str:
    client = get_client()
    await client.connect()
    try:
        if not await client.is_user_authorized():
            return "Ошибка: сессия Telegram не авторизована."

        if name == "get_unread_messages":
            limit_chats = int(args.get("limit_chats", 15))
            messages_per_chat = int(args.get("messages_per_chat", 10))
            dialogs = await client.get_dialogs(limit=100)
            result = []
            count = 0
            for d in dialogs:
                if d.unread_count > 0:
                    count += 1
                    if count > limit_chats:
                        break
                    chat_type = "Канал" if d.is_channel and not d.is_group else ("Группа" if d.is_group else "Личка")
                    msgs = await client.get_messages(d.entity, limit=min(d.unread_count, messages_per_chat))
                    chat_block = [f"### [{chat_type}] {d.name} (непрочитано: {d.unread_count})"]
                    for m in reversed(msgs):
                        if m.text:
                            sender = f"{getattr(m.sender, 'first_name', 'User')}: " if (d.is_group and m.sender) else ""
                            clean_text = m.text.replace("\n", " ")[:400]
                            chat_block.append(f"- {sender}{clean_text}")
                    result.append("\n".join(chat_block))
            return "\n\n".join(result) if result else "Непрочитанных сообщений нет."

        elif name == "list_dialogs":
            query = args.get("query", "").lower().strip()
            limit = int(args.get("limit", 30))
            dialogs = await client.get_dialogs(limit=None)
            lines = []
            for d in dialogs:
                title = d.name or ""
                username = getattr(d.entity, "username", None)
                uname_str = f"@{username}" if username else "без username"
                if not query or query in title.lower() or (username and query in username.lower()):
                    lines.append(f"- Название: '{title}' | {uname_str} | ID: {d.id}")
                    if len(lines) >= limit:
                        break
            return "\n".join(lines) if lines else "Подходящие чаты не найдены."

        elif name == "read_chat_messages":
            chat_query = str(args.get("chat_query", "")).strip()
            limit = int(args.get("limit", 15))
            search_text = args.get("search_text", "")
            target_entity = None
            target_name = chat_query

            if chat_query.lstrip("-").isdigit():
                target_id = int(chat_query)
                dialogs = await client.get_dialogs(limit=None)
                for d in dialogs:
                    if d.id == target_id:
                        target_entity = d.entity
                        target_name = d.name
                        break
            elif chat_query.startswith("@"):
                target_entity = await client.get_entity(chat_query)
                target_name = getattr(target_entity, "title", getattr(target_entity, "first_name", chat_query))
            else:
                dialogs = await client.get_dialogs(limit=None)
                q_lower = chat_query.lower()
                for d in dialogs:
                    if (d.name or "").lower().strip() == q_lower:
                        target_entity = d.entity
                        target_name = d.name
                        break
                if not target_entity:
                    for d in dialogs:
                        if q_lower in (d.name or "").lower():
                            target_entity = d.entity
                            target_name = d.name
                            break

            if not target_entity:
                return f"Чат или канал '{chat_query}' не найден."

            msgs = await client.get_messages(target_entity, limit=limit, search=search_text or None)
            if not msgs:
                return f"В чате '{target_name}' сообщений не найдено."

            lines = [f"### Сообщения из: {target_name} (ID: {getattr(target_entity, 'id', '')})"]
            for m in reversed(msgs):
                if m.text:
                    sender = f"{getattr(m.sender, 'first_name', 'User')}: " if m.sender else ""
                    clean_text = m.text.replace("\n", " ")[:500]
                    lines.append(f"- [{m.date.strftime('%Y-%m-%d %H:%M')}] {sender}{clean_text}")
            return "\n".join(lines)

        elif name == "search_global_messages":
            query = args.get("query", "")
            limit = int(args.get("limit", 15))
            chat_type = args.get("chat_type", "all")

            if chat_type == "all":
                msgs = await client.get_messages(None, limit=limit, search=query)
                if not msgs:
                    return f"По запросу '{query}' ничего не найдено."
                lines = [f"### Гlobal search for '{query}':"]
                for m in msgs:
                    if m.text:
                        chat_name = getattr(m.chat, "title", getattr(m.chat, "first_name", "Чат"))
                        clean_text = m.text.replace("\n", " ")[:400]
                        lines.append(f"- [{chat_name} | {m.date.strftime('%Y-%m-%d %H:%M')}] {clean_text}")
                return "\n".join(lines)
            else:
                dialogs = await client.get_dialogs(limit=150)
                lines = [f"### Поиск по запросу '{query}' (фильтр: {chat_type}):"]
                found = 0
                for d in dialogs:
                    if chat_type == "private" and not (d.is_user and not getattr(d.entity, "bot", False)):
                        continue
                    if chat_type == "group" and not d.is_group:
                        continue
                    if chat_type == "channel" and not (d.is_channel and not d.is_group):
                        continue

                    msgs = await client.get_messages(d.entity, limit=5, search=query)
                    for m in msgs:
                        if m.text:
                            clean_text = m.text.replace("\n", " ")[:400]
                            lines.append(f"- [{d.name} | {m.date.strftime('%Y-%m-%d %H:%M')}] {clean_text}")
                            found += 1
                            if found >= limit:
                                break
                if found >= limit:
                    return "\n".join(lines)
                return f"В категории '{chat_type}' по запросу '{query}' ничего не найдено."

        return f"Неизвестный инструмент: {name}"
    finally:
        await client.disconnect()

def send_response(msg_id, result=None, error=None):
    payload = {"jsonrpc": "2.0", "id": msg_id}
    if error is not None:
        payload["error"] = error
    else:
        payload["result"] = result
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except Exception:
            continue
        method = req.get("method")
        msg_id = req.get("id")
        if msg_id is None:
            continue
        if method == "initialize":
            send_response(msg_id, {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "TelegramReader", "version": "1.0.0"},
            })
        elif method == "tools/list":
            send_response(msg_id, {"tools": TOOLS})
        elif method == "tools/call":
            params = req.get("params", {})
            tool_name = params.get("name", "")
            tool_args = params.get("arguments", {})
            try:
                text_out = asyncio.run(run_tool(tool_name, tool_args))
                send_response(msg_id, {"content": [{"type": "text", "text": text_out}]})
            except Exception as e:
                send_response(msg_id, {"content": [{"type": "text", "text": f"Ошибка выполнения: {e}"}], "isError": True})
        else:
            send_response(msg_id, {})

if __name__ == "__main__":
    main()
