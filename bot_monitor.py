import logging
import os
import asyncio
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from playwright.async_api import async_playwright

TOKEN = "8473861493:AAH8G9mOub_SNGuDYbQZMPUnCd-qFybnABQ"
USERNAME = "bangjo10"
PASSWORD = "Menang123"

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- DAFTAR LENGKAP PROVIDER ---
ALL_CATEGORIES = {
    "SLOT": {
        "url": "https://pokerboya.com/egames",
        "providers": [
            {"name": "PGSOFT", "selector": "a[href='#vendor_PGSOFT']"},
            {"name": "Pragmatic Play", "selector": "a[href='#vendor_PragmaticPlay']"},
            {"name": "CQ9", "selector": "a[href='#vendor_CQ9']"},
            {"name": "5G", "selector": "a[href='#vendor_5G']"},
            {"name": "JILI", "selector": "a[href='#vendor_JILI']"},
            {"name": "Nextspin", "selector": "a[href='#vendor_Nextspin']"},
            {"name": "Playtech", "selector": "a[href='#vendor_Playtech']"},
            {"name": "Fast Spin", "selector": "a[href='#vendor_FastSpin']"},
            {"name": "RTG Slots", "selector": "a[href='#vendor_RTGSlots']"},
            {"name": "Pragmatic Play POP", "selector": "a[href='#vendor_PragmaticPlayPOP']"},
            {"name": "NLC", "selector": "a[href='#vendor_NLC']"},
            {"name": "Spadegaming", "selector": "a[href='#vendor_Spadegaming']"},
            {"name": "Hotdog Gaming", "selector": "a[href='#vendor_HotdogGaming']"},
            {"name": "Microgaming", "selector": "a[href='#vendor_Microgaming']"},
            {"name": "Hacksaw", "selector": "a[href='#vendor_Hacksaw']"},
            {"name": "Habanero", "selector": "a[href='#vendor_Habanero']"},
            {"name": "Playstar", "selector": "a[href='#vendor_Playstar']"},
            {"name": "Booming Games", "selector": "a[href='#vendor_BoomingGames']"},
            {"name": "JDB", "selector": "a[href='#vendor_JDB']"},
            {"name": "BNG", "selector": "a[href='#vendor_BNG']"},
            {"name": "Spinomenal", "selector": "a[href='#vendor_Spinomenal']"},
            {"name": "Joker Gaming", "selector": "a[href='#vendor_JokerGaming']"},
            {"name": "Red Tiger", "selector": "a[href='#vendor_RedTiger']"},
            {"name": "SABA", "selector": "a[href='#vendor_SABA']"},
            {"name": "PopOk Gaming", "selector": "a[href='#vendor_PopOkGaming']"},
            {"name": "YGG", "selector": "a[href='#vendor_YGG']"},
            {"name": "Funky Games", "selector": "a[href='#vendor_FunkyGames']"},
            {"name": "Funta Gaming", "selector": "a[href='#vendor_FuntaGaming']"},
            {"name": "9G", "selector": "a[href='#vendor_9G']"},
            {"name": "Top Trend Gaming", "selector": "a[href='#vendor_TopTrendGaming']"},
            {"name": "GamePlayInt", "selector": "a[href='#vendor_GamePlayInt']"},
            {"name": "NetEnt", "selector": "a[href='#vendor_NetEnt']"},
            {"name": "PNG", "selector": "a[href='#vendor_PNG']"},
            {"name": "Big Time Gaming", "selector": "a[href='#vendor_BigTimeGaming']"},
            {"name": "One Game", "selector": "a[href='#vendor_OneGame']"},
            {"name": "Skywind", "selector": "a[href='#vendor_Skywind']"},
            {"name": "SBO Slot", "selector": "a[href='#vendor_SBOSlot']"},
            {"name": "SimplePlay", "selector": "a[href='#vendor_SimplePlay']"},
            {"name": "Reevo", "selector": "a[href='#vendor_Reevo']"},
            {"name": "OneTouch", "selector": "a[href='#vendor_OneTouch']"},
            {"name": "OGPS Slot Games", "selector": "a[href='#vendor_OGPSSlotGames']"},
        ]
    },
    "ARCADE": {
        "url": "https://pokerboya.com/arcade",
        "providers": [
            {"name": "Pragmatic Play", "selector": "a[href='#vendor_PragmaticPlay']"},
            {"name": "PGSOFT", "selector": "a[href='#vendor_PGSOFT']"},
            {"name": "JILI", "selector": "a[href='#vendor_JILI']"},
            {"name": "Canvas Gaming", "selector": "a[href='#vendor_CanvasGaming']"},
            {"name": "JDB", "selector": "a[href='#vendor_JDB']"},
            {"name": "CQ9", "selector": "a[href='#vendor_CQ9']"},
            {"name": "BGM Fishing", "selector": "a[href='#vendor_BGMFishing']"},
            {"name": "SimplePlay", "selector": "a[href='#vendor_SimplePlay']"},
            {"name": "RTG Slots", "selector": "a[href='#vendor_RTGSlots']"},
            {"name": "SABA", "selector": "a[href='#vendor_SABA']"},
            {"name": "MG Arcade", "selector": "a[href='#vendor_MGArcade']"},
            {"name": "PopOk Gaming", "selector": "a[href='#vendor_PopOkGaming']"},
            {"name": "Spadegaming", "selector": "a[href='#vendor_Spadegaming']"},
            {"name": "Funky Games", "selector": "a[href='#vendor_FunkyGames']"},
            {"name": "YGG", "selector": "a[href='#vendor_YGG']"},
            {"name": "Joker Gaming", "selector": "a[href='#vendor_JokerGaming']"},
            {"name": "Joker Fishing", "selector": "a[href='#vendor_JokerFishing']"},
            {"name": "Skywind", "selector": "a[href='#vendor_Skywind']"},
            {"name": "Hotdog Gaming", "selector": "a[href='#vendor_HotdogGaming']"},
            {"name": "Aviatrix", "selector": "a[href='#vendor_Aviatrix']"},
            {"name": "Fast Spin", "selector": "a[href='#vendor_FastSpin']"},
            {"name": "Evolution", "selector": "a[href='#vendor_Evolution']"},
            {"name": "Red Tiger", "selector": "a[href='#vendor_RedTiger']"},
            {"name": "Habanero", "selector": "a[href='#vendor_Habanero']"},
            {"name": "GamePlayInt", "selector": "a[href='#vendor_GamePlayInt']"},
            {"name": "Funta Gaming", "selector": "a[href='#vendor_FuntaGaming']"},
            {"name": "OneTouch", "selector": "a[href='#vendor_OneTouch']"},
            {"name": "NetEnt", "selector": "a[href='#vendor_NetEnt']"},
            {"name": "Nextspin", "selector": "a[href='#vendor_Nextspin']"},
            {"name": "9G", "selector": "a[href='#vendor_9G']"},
            {"name": "Playtech", "selector": "a[href='#vendor_Playtech']"},
            {"name": "Reevo", "selector": "a[href='#vendor_Reevo']"},
            {"name": "PNG", "selector": "a[href='#vendor_PNG']"},
        ]
    },
    "SPORTSBOOK": {
        "url": "https://pokerboya.com/sportsbook",
        "providers": [
            {"name": "BPG", "selector": "a[onclick*=\"'BPG','SPORTSBOOK'\"]"},
            {"name": "WIN568", "selector": "a[onclick*=\"'WIN568','win568SportsBook'\"]"},
            {"name": "CMD", "selector": "a[onclick*=\"'CMD','wlhkb'\"]"},
            {"name": "BTI", "selector": "a[onclick*=\"'BTI','hkb'\"]"},
            {"name": "IMONE SB", "selector": "a[onclick*=\"'IMONE#301','IMSB'\"]"},
            {"name": "eSportsBull", "selector": "a[onclick*=\"'IMONE#401','eSportsBull'\"]"},
            {"name": "TFG", "selector": "a[onclick*=\"'TFG','hkb'\"]"},
        ]
    },
    "CASINO": {
        "url": "https://pokerboya.com/livecasino",
        "providers": [
            {"name": "Pragmatic Play", "selector": "a[onclick*=\"'PP','101'\"]"},
            {"name": "Evolution", "selector": "a[onclick*=\"'EVO','lobby-baccarat_sicbo'\"]"},
            {"name": "Dream Gaming", "selector": "a[onclick*=\"'DG','baccarat'\"]"},
            {"name": "WIN568 Casino", "selector": "a[onclick*=\"'WIN568','win568Casino'\"]"},
            {"name": "OGPS", "selector": "a[onclick*=\"'OGPS','1'\"]"},
            {"name": "PTIM", "selector": "a[onclick*=\"'PTIM','bal'\"]"},
            {"name": "SAG", "selector": "a[onclick*=\"'SAG','saglobby'\"]"},
            {"name": "Microgaming", "selector": "a[onclick*=\"'MG','MGL_GRAND_LobbyAll'\"]"},
            {"name": "PopOk Gaming", "selector": "a[onclick*=\"'POPOK','500'\"]"},
            {"name": "HG", "selector": "a[onclick*=\"'HG','0000000000000004'\"]"},
            {"name": "VG", "selector": "a[onclick*=\"'VG','0'\"]"},
            {"name": "WMC", "selector": "a[onclick*=\"'WMC','livecasino'\"]"},
            {"name": "Ezugi", "selector": "a[onclick*=\"'EZUGI','livecasino'\"]"},
            {"name": "PA1", "selector": "a[onclick*=\"'PA1','0'\"]"},
            {"name": "BGM", "selector": "a[onclick*=\"'BGM','bgm_lobby'\"]"},
            {"name": "BPG (Allbet)", "selector": "a[onclick*=\"'BPG','Allbet'\"]"},
            {"name": "CQ9", "selector": "a[onclick*=\"'CQ9','GINKGO01'\"]"},
            {"name": "Skywind", "selector": "a[onclick*=\"'SKW','skywind_lobby'\"]"},
            {"name": "GPI", "selector": "a[onclick*=\"'GPI','livecasino'\"]"},
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

async def check_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Pilih kategori!")
    cat_name = context.args[0].upper()
    if cat_name not in ALL_CATEGORIES: return await update.message.reply_text("Kategori tidak valid.")
    msg = await update.message.reply_text(f"Mengecek {cat_name}...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context_browser = await browser.new_context(storage_state="session.json") if os.path.exists("session.json") else await browser.new_context()
        page = await context_browser.new_page()
        await page.goto(ALL_CATEGORIES[cat_name]['url'], wait_until="networkidle")
        results = []
        for p_data in ALL_CATEGORIES[cat_name]['providers']:
            status = await run_check(p_data, page, context_browser)
            results.append(f"• {p_data['name']}: {status}")
            if len(results) % 5 == 0: await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=msg.message_id, text=f"Sedang mengecek {cat_name}...\n\n" + "\n".join(results))
        final_text = f"Hasil {cat_name}:\n\n" + "\n".join(results)
        for i in range(0, len(final_text), 4000): await update.message.reply_text(final_text[i:i+4000])
        await context_browser.storage_state(path="session.json")
        await browser.close()

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.bot.delete_webhook(drop_pending_updates=True)
    app.add_handler(CommandHandler("check", check_category))
    app.run_polling(drop_pending_updates=True)