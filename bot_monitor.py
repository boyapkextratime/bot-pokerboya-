import logging
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

TOKEN = "8473861493:AAEWKeVFXJN3ZjshjGXUlMkho3rLW_Q-oDc"
USERNAME = "bangjo10"
PASSWORD = "Menang123"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- WEB SERVER (AGAR RENDER TIDAK KOMPLAIN) ---
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="Bot is running!"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

# --- DAFTAR PROVIDER ---
ALL_CATEGORIES = {
    "SLOT": {
        "url": "https://pokerboya.com/egames",
        "providers": [
            {"name": "PGSOFT", "selector": "a[href='#vendor_PGSOFT']"},
            {"name": "Pragmatic Play", "selector": "a[href='#vendor_PragmaticPlay']"},
            {"name": "CQ9", "selector": "a[href='#vendor_CQ9']"},
        ]
    },
    "ARCADE": {
        "url": "https://pokerboya.com/arcade",
        "providers": [
            {"name": "JILI", "selector": "a[href='#vendor_JILI']"},
            {"name": "Pragmatic Play", "selector": "a[href='#vendor_PragmaticPlay']"},
            {"name": "PGSOFT", "selector": "a[href='#vendor_PGSOFT']"},
        ]
    },
    "SPORTSBOOK": {
        "url": "https://pokerboya.com/sportsbook",
        "providers": [
            {"name": "BPG", "selector": "a[onclick*=\"'BPG','SPORTSBOOK'\"]"},
            {"name": "WIN568", "selector": "a[onclick*=\"'WIN568','win568SportsBook'\"]"},
            {"name": "CMD", "selector": "a[onclick*=\"'CMD','wlhkb'\"]"},
        ]
    },
    "CASINO": {
        "url": "https://pokerboya.com/livecasino",
        "providers": [
            {"name": "Pragmatic Play", "selector": "a[onclick*=\"'PP','101'\"]"},
            {"name": "Evolution", "selector": "a[onclick*=\"'EVO','lobby-baccarat_sicbo'\"]"},
            {"name": "Dream Gaming", "selector": "a[onclick*=\"'DG','baccarat'\"]"},
        ]
    },
    "SABUNG": {
        "url": "https://pokerboya.com/cockfight",
        "providers": [
            {"name": "GA28", "selector": "a[onclick*=\"'GA28','ga28'\"]"},
            {"name": "SV388", "selector": "a[onclick*=\"'SV388','SV-LIVE-001'\"]"},
            {"name": "WS168", "selector": "a[onclick*=\"'WS168','1-ws168'\"]"},
        ]
    }
}

async def login_otomatis(page):
    try:
        await page.goto("https://pokerboya.com/", wait_until="networkidle")
        if await page.query_selector("input[name='username']"):
            await page.fill("input[name='username']", USERNAME)
            await page.fill("input[name='password']", PASSWORD)
            await page.click("button[type='submit']")
            await page.wait_for_timeout(5000)
    except: pass

async def run_check(p_data, page, context_browser):
    for attempt in range(3):
        try:
            if page.is_closed(): return "FAILED (Browser Closed)"
            popup = await page.query_selector("button[aria-label='Close'], .modal-close, .close")
            if popup: await popup.click()
            await page.click(p_data['selector'], timeout=10000)
            await page.wait_for_timeout(6000)
            if len(context_browser.pages) > 1 or len(page.frames) > 1 or await page.query_selector("iframe"):
                return "AMAN"
            raise Exception("Lobby tidak muncul")
        except:
            await page.reload(wait_until="networkidle")
            await page.wait_for_timeout(5000)
    return "FAILED"

async def start(update, context):
    await update.message.reply_text("Bot Aktif! Gunakan /check [KATEGORI]")

async def login_manual(update, context):
    await update.message.reply_text("Silakan login di laptop Anda agar session.json terupdate.")

async def check_category(update, context):
    if not context.args: return await update.message.reply_text("Pilih kategori!")
    cat_name = context.args[0].upper()
    if cat_name not in ALL_CATEGORIES: return await update.message.reply_text("Kategori tidak valid.")
    msg = await update.message.reply_text(f"Mengecek {cat_name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_browser = await browser.new_context(storage_state="session.json") if os.path.exists("session.json") else await browser.new_context()
        page = await context_browser.new_page()
        await login_otomatis(page)
        await page.goto(ALL_CATEGORIES[cat_name]['url'], wait_until="networkidle")
        results = []
        for p_data in ALL_CATEGORIES[cat_name]['providers']:
            status = await run_check(p_data, page, context_browser)
            results.append(f"• {p_data['name']}: {status}")
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"Hasil {cat_name}:\n\n" + "\n".join(results))
        await context_browser.storage_state(path="session.json")
        await browser.close()

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login_manual))
    app.add_handler(CommandHandler("check", check_category))
    
    # Menjalankan polling
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)
    print("Bot sudah jalan!")
    
    # Keep alive
    await asyncio.Event().wait()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    loop.run_until_complete(main())
