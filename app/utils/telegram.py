import html, json, logging
from datetime import datetime, timedelta, timezone
from urllib import request

from app.utils.config import settings

log = logging.getLogger("aljabr.telegram")
TASHKENT = timezone(timedelta(hours=5))
PLANS = {"standard": "Standart", "pro": "Pro"}


def _esc(v: str, n: int) -> str:
    return html.escape(v.strip()[:n])


def build_message(*, reference, product, plan, name, phone, description) -> str:
    now = datetime.now(TASHKENT).strftime("%d.%m.%Y %H:%M")
    return (
        "\U0001F195 <b>Yangi ariza</b>\n\n"
        f"<b>Mahsulot:</b> {_esc(product, 120)}\n"
        f"<b>Tarif:</b> {PLANS.get(plan, _esc(plan, 20))}\n"
        f"<b>Ism:</b> {_esc(name, 100)}\n"
        f"<b>Telefon:</b> {_esc(phone, 25)}\n\n"
        f"{_esc(description, 2500)}\n\n"
        f"<code>{_esc(reference, 40)}</code> \u00b7 {now}"
    )


def send_telegram(text: str) -> None:
    token, chat_id = settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID
    if not token or not chat_id:
        log.warning("Telegram sozlanmagan")
        return
    payload = json.dumps({"chat_id": chat_id, "text": text[:4000],
                          "parse_mode": "HTML", "disable_web_page_preview": True}).encode()
    req = request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=payload,
                          headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=8):
            pass
    except Exception as exc:
        log.error("Telegramga yuborib bo'lmadi: %s", type(exc).__name__)