# Bionic Windows Toolkit: Telegram Read-Only MCP & Agent Skills

Лёгкий и безопасный набор инструментов для локальных ИИ-агентов в **LM Studio Bionic** (и любых других MCP-совместимых клиентов) на **Windows 11**.

## Что входит в проект

1. **`telegram_mcp.py`** — автономный однофайловый MCP-сервер на чистом JSON-RPC + `Telethon`:
   - **Без зависимости от `FastMCP` / `anyio`:** не зависает при чтении `stdin` на Windows и свежих версиях Python (3.13–3.15).
   - **Безопасный режим Read-Only (4 инструмента):** не может случайно отправить или удалить сообщения и не сбрасывает статус непрочитанного.
   - **Поддержка прокси из коробки:** работает через локальный **`tg ws proxy` (MTProto-прокси)** (`ConnectionTcpMTProxyRandomizedIntermediate`), `SOCKS5`, `HTTP` или напрямую.
   - **Минимальный расход контекста:** идеально подходит для локальных моделей с окном контекста 16K–32K (например, Gemma 4 26B A4B).

2. **`skills/`** — набор проверенных инструкций (`SKILL.md`) для Bionic на Windows:
   - `windows-powershell-rules` — переводит агента с Linux/Bash-команд на нативный синтаксис Windows PowerShell и обходит ограничения встроенной песочницы Pyodide.
   - `memory-manager` — точные JSON-схемы для `@modelcontextprotocol/server-memory`, исключающие ошибки валидации графа знаний.
   - `obsidian-manager` — безопасная организация заметок в хранилище Obsidian с автоподстановкой даты.
   - `file-processor` — автоматический разбор `.xlsx`, `.docx` и `.pdf` через локальные библиотеки Python.

---

## Установка и настройка в PowerShell

### 1. Установите зависимости (Python 3.10+)
Откройте **PowerShell** и выполните:
```powershell
pip install telethon "python-socks[asyncio]"
```

### 2. Выполните одноразовую авторизацию в Telegram
Создайте файл сессии на диске (в примере ниже используется подключение через локальный `tg ws proxy` на порту `1443`; для прямого подключения уберите аргументы `connection` и `proxy`):
```powershell
python -c "from telethon import TelegramClient, connection; c = TelegramClient(r'C:\Users\<USER>\.lmstudio\bionic_tg_session', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e', connection=connection.ConnectionTcpMTProxyRandomizedIntermediate, proxy=('127.0.0.1', 1443, '<YOUR_PROXY_SECRET>')); c.start(phone=lambda: input('Телефон: '), code_callback=lambda: input('Код: '), password=lambda: input('Пароль 2FA: ')); print('Авторизация завершена!'); c.disconnect()"
```
> **Важно:** Никогда не передавайте файл `*.session` третьим лицам и не загружайте его в публичные репозитории.

### 3. Подключите сервер в LM Studio Bionic (`Integrations → MCP → Add MCP`)
* **Name:** `telegram`
* **Command:** полный путь к вашему `python.exe` (узнать можно в PowerShell через `(Get-Command python).Source`)
* **Arguments:** полный путь к скрипту `telegram_mcp.py`
* **Environment Variables (включив `Show advanced options`):**
  * `TG_SESSION_PATH` — путь к файлу сессии без расширения `.session`
  * `TG_PROXY_TYPE` — `mtproto` (для **`tg ws proxy`**), `socks5` или `http` (оставьте пустым для прямого подключения)
  * `TG_PROXY_HOST` — `127.0.0.1`
  * `TG_PROXY_PORT` — порт вашего локального прокси (например, `1443` для `tg ws proxy` или `1080` для SOCKS5)
  * `TG_PROXY_SECRET` — секретный ключ прокси из настроек клиента (только для `mtproto`)

---

## Доступные инструменты MCP

* `get_unread_messages` — собирает непрочитанные сообщения из личных чатов, групп и каналов (не отмечая их прочитанными).
* `list_dialogs` — находит нужные чаты и каналы с их точными названиями, `@username` и числовыми ID.
* `read_chat_messages` — читает последние посты/сообщения или ищет по ключевому слову внутри выбранного чата.
* `search_global_messages` — глобальный поиск по сообщениям с фильтром по типу чата (`all`, `private`, `group`, `channel`).

---

*Проект разработан и протестирован на локальной связке Windows 11 + LM Studio Bionic (Gemma 4 26B A4B) в соавторстве с ИИ-ассистентом Gemini (Google).*
