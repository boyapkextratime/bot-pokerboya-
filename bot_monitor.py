import logging
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

TOKEN = "8473861493:AAHGHJg50pyjG1aWiyueS-GXkW9txQYBerc"
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- WEB SERVER UNTUK RENDER ---
async def health_check(request):
    return web.Response(text="Bot is running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    # Render menggunakan port yang diberikan oleh environment variable atau default 10000
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
            {"name": "Pragmatic Play", "selector": "a[href='#vendor_PragmaticPlay']"},
            {"name": "PGSOFT", "selector": "a[href='#vendor_PGSOFT']"},
            {"name": "JILI", "selector": "a[href='#vendor_JILI']"},
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

async def run_check(p_data, page, context_browser):
    for attempt in range(3):
        try:
            if page.is_closed(): return "FAILED (Browser Closed)"
            # Anti-Popup
            popup_close = await page.query_selector("button[aria-label='Close'], .modal-close, .close")
            if popup_close: await popup_close.click()

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

async def check_category(update, context):
    if not context.args: return await update.message.reply_text("Pilih kategori!")
    cat_name = context.args[0].upper()
    if cat_name not in ALL_CATEGORIES: return await update.message.reply_text("Kategori tidak valid.")

    msg = await update.message.reply_text(f"Mengecek {cat_name}...")
    
    async with async_playwright() as p:
        # headless=True wajib untuk Render/Server agar tidak error
        browser = await p.chromium.launch(headless=True)
        context_browser = await browser.new_context(storage_state="session.json") if os.path.exists("session.json") else await browser.new_context()
        page = await context_browser.new_page()
        await page.goto(ALL_CATEGORIES[cat_name]['url'], wait_until="networkidle")
        
        results = []
        for p_data in ALL_CATEGORIES[cat_name]['providers']:
            status = await run_check(p_data, page, context_browser)
            results.append(f"• {p_data['name']}: {status}")
        
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"Hasil {cat_name}:\n\n" + "\n".join(results))
        await context_browser.storage_state(path="session.json")
        await browser.close()

if __name__ == '__main__':
    # Jalankan web server di background
    loop = asyncio.get_event_loop()
    loop.create_task(start_web_server())
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check_category))
    
    print("Bot sudah jalan!")
    app.run_polling()
