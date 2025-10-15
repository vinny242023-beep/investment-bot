import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

BOT_TOKEN = "8203632125:AAFl3OqXf4mKeijmA1-YFmJGP9UMUbCxl0I"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- БАЗА ДАННЫХ ФИНАНСОВЫХ ЗНАНИЙ ---

BOOKS_MENU = [
    "Самый богатый человек в Вавилоне",
    "Разумный инвестор",
    "Думай и богатей"
]

BOOKS_CONTENT = {
    "Самый богатый человек в Вавилоне":
    """
    Глава 1. Деньги любят счёт.
    «Начни копить хотя бы 10% дохода. Не важно сколько ты зарабатываешь — откладывай всегда.»

    Глава 2. Управление затратами.
    «Контролируй желания. Не трать на то, без чего можно прожить.»

    Глава 3. Заставь деньги работать.
    «Пусть каждая монета трудится и приносит новые деньги!»

    Глава 4. Береги капитал от убытков.
    «Не рискуй сбережениями, выбирай надёжные вложения.»

    Глава 5. Инвестируй разумно.
    «Умей отличить хорошие вложения от плохих. Свой опыт — твоя главная ценность.»

    Глава 6. Защита денег и знаний.
    «Прислушивайся к совету специалистов. Учись у мастеров.»

    Глава 7. Финансовая мотивация.
    «Для богатства требуется терпение, дисциплина и регулярность. Не сдавайся!»
    """,

    "Разумный инвестор":
    """
    Глава 1. Основы инвестирования.
    «Всегда планируй, на какой срок и с каким риском ты вкладываешь деньги.»

    Глава 2. Психология vs. Математика
    «Главный враг инвестора — не рынок, а собственные эмоции: страх и жадность.»

    Глава 3. Маржа безопасности.
    «Покупай актив с запасом — по цене ниже его реальной стоимости.»

    Глава 4. Долгосрочные стратегии.
    «Лучше стабильный 8% годовых с капитализацией, чем краткосрочные спекуляции.»

    Глава 5. Защита от инфляции.
    «Диверсифицируй активы — акции, облигации, валюта, недвижимость.»

    Глава 6. Ошибки и уроки.
    «Успех приходит к тем, кто терпелив и умеет учиться на ошибках других.»
    """,

    "Думай и богатей":
    """
    Глава 1. Мечтай и действуй!
    «Сильное желание богатства — первый шаг к реальным результатам.»

    Глава 2. Верь, что это возможно.
    «Настойчиво повторяй свои цели, визуализируй успех.»

    Глава 3. Планируй и не бойся ошибаться.
    «Без чёткого плана не бывает пути к богатству.»

    Глава 4. Учись на каждом поражении.
    «Каждая неудача — это опыт и шаг к будущей победе.»

    Глава 5. Мастермайнд.
    «Окружи себя такими же целеустремлёнными людьми.»

    Глава 6. Энтузиазм и постоянство.
    «Ежедневные действия и энергия — главное топливо богатого человека.»
    """
}

INVEST_TIPS = [
    "Вкладывай только свободные деньги.",
    "Сначала создай подушку безопасности (3-6 месяцев расходов).",
    "Автоматизируй процесс: инвестируй каждый месяц.",
    "Покупай ETF на индекс — это просто и безопасно для новичка.",
    "Не пытайся предсказать рост или падение рынка.",
    "Диверсифицируй — не держи всё в одном активе.",
    "Фиксируй ошибки в дневнике инвестора и регулярно пересматривай план.",
    "Не паникуй на просадках — рынок растёт долгосрочно.",
    "Минимизируй комиссии и лишние операции.",
    "Смотри на долгосрочный результат, а не быструю прибыль."
]

MONEY_MANAGEMENT_TIPS = [
    "Сделай привычкой откладывать 10% дохода сразу после получения.",
    "Раздели деньги: расходы, инвестиции, развлечения, обучение, помощь другим.",
    "Составь домашний бюджет и фиксируй все траты хотя бы месяц.",
    "Покупай новые вещи только по действительно важной необходимости.",
    "Оцени каждую крупную покупку через «Правило 24 часов»: переночуй с мыслью.",
    "Минимизируй кредиты и долги — выплачивай сначала с крупными процентами.",
    "Раз в полгода анализируй финансовые цели и корректируй бюджет.",
    "Учись финансовой грамотности — читай, слушай подкасты, проходи курсы."
]

MOTIVATION = [
    "Каждый богатый человек когда-то был бедным. Всё зависит от тебя!",
    "Если ты начал — ты уже лучше, чем 90% остальных, кто только думает.",
    "Сила — в системности, а не в размере стартового капитала.",
    "Большое состояние — это результат тысячи маленьких шагов.",
    "Не бойся ошибаться — бойся никогда не попробовать.",
    "Время — твой главный союзник: инвестируй сегодня, чтобы пожать плоды завтра.",
    "Ты контролируешь не рынок, но свой вклад и свою дисциплину.",
    "Финансовая свобода — это не только про деньги, но про выбор и уверенность."
]

FAQ = [
    "Что делать, если нет больших доходов? — Начни с малого! Даже 500₽ в месяц — путь к капиталу.",
    "Нужно ли быть финансистом? — Нет. Главное — научиться базовым правилам, инвестировать регулярно.",
    "Что делать при падении рынка? — Не паниковать, не продавать в убыток. Лучше докупай активы.",
    "Какой финансовой литературы доверять? — Классика: Клейсон, Грэм, Хилл. Изучай опыт практиков.",
    "В чем разница между инвестор и спекулянт? — Инвестор создает капитал на года, спекулянт ловит краткий заработок с большим риском.",
]

# --- КНОПКИ МЕНЮ ---

def get_main_menu_keyboard():
    return ReplyKeyboardMarkup([
        ["📚 Книги", "📝 FAQ", "🧩 Советы"],
        ["💡 Управление деньгами", "🔥 Мотивация", "Главное меню"],
    ], resize_keyboard=True)

def get_books_keyboard():
    return ReplyKeyboardMarkup([
        ["Самый богатый человек в Вавилоне"],
        ["Разумный инвестор"],
        ["Думай и богатей"],
        ["Главное меню"]
    ], resize_keyboard=True)

class InvestmentSuperBot:
    def __init__(self):
        self.init_db()

    def init_db(self):
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS user_stats (user_id INTEGER PRIMARY KEY, name TEXT, questions_count INTEGER, last_visit TEXT)"
        )
        con.commit()
        con.close()

    def update_user_stat(self, user_id, name):
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(
            "INSERT OR IGNORE INTO user_stats (user_id, name, questions_count, last_visit) VALUES (?, ?, 0, datetime('now'))",
            (user_id, name)
        )
        cur.execute(
            "UPDATE user_stats SET last_visit=datetime('now') WHERE user_id=?",
            (user_id,)
        )
        con.commit()
        con.close()

    def increment_questions(self, user_id):
        con = sqlite3.connect("users.db")
        cur = con.cursor()
        cur.execute(
            "UPDATE user_stats SET questions_count = questions_count + 1 WHERE user_id=?",
            (user_id,)
        )
        con.commit()
        con.close()

    # ==== КОМАНДЫ ====

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        self.update_user_stat(user.id, user.first_name)
        text = (
            f"Привет, {user.first_name} 👋\n"
            "Я бот-помощник по инвестициям, денежным привычкам и финансовой мотивации!\n"
            "Могу поделиться лучшими советами и знаниями из книг.\n"
            "Воспользуйся меню или напиши название интересующей книги, тему, или просто вопрос."
        )
        await update.message.reply_text(text, reply_markup=get_main_menu_keyboard())

    async def show_books(self, update: Update, context: CallbackContext):
        await update.message.reply_text(
            "📚 Выбери книгу для чтения (цитаты и главы):",
            reply_markup=get_books_keyboard()
        )

    async def show_faq(self, update: Update, context: CallbackContext):
        faq_text = "\n".join(f"• {q}" for q in FAQ)
        await update.message.reply_text(f"📝 Частые вопросы:\n{faq_text}", reply_markup=get_main_menu_keyboard())

    async def show_tips(self, update: Update, context: CallbackContext):
        tips_text = "\n".join(f"➕ {tip}" for tip in INVEST_TIPS)
        await update.message.reply_text(f"🧩 Советы инвестору:\n{tips_text}", reply_markup=get_main_menu_keyboard())

    async def show_money(self, update: Update, context: CallbackContext):
        mm_text = "\n".join(f"💡 {tip}" for tip in MONEY_MANAGEMENT_TIPS)
        await update.message.reply_text(f"💡 Советы по управлению деньгами:\n{mm_text}", reply_markup=get_main_menu_keyboard())

    async def show_motivation(self, update: Update, context: CallbackContext):
        mot_text = "\n".join(f"🔥 {m}" for m in MOTIVATION)
        await update.message.reply_text(f"🔥 Мотивация для тебя:\n{mot_text}", reply_markup=get_main_menu_keyboard())

    async def show_book_content(self, update: Update, context: CallbackContext):
        msg = update.message.text.strip()
        for book in BOOKS_MENU:
            if book.lower() in msg.lower():
                await update.message.reply_text(
                    f"📖 {book}\n{BOOKS_CONTENT[book]}",
                    reply_markup=get_books_keyboard()
                )
                return
        await self.show_books(update, context)

    async def handle_message(self, update: Update, context: CallbackContext):
        user = update.effective_user
        self.update_user_stat(user.id, user.first_name)
        self.increment_questions(user.id)
        msg = update.message.text.strip().lower()

        if "faq" in msg:
            await self.show_faq(update, context)
            return
        if "совет" in msg:
            await self.show_tips(update, context)
            return
        if "книг" in msg or "глав" in msg or "вавилон" in msg or "инвестор" in msg or "думай" in msg:
            await self.show_books(update, context)
            return
        if any(book.lower() in msg for book in BOOKS_MENU):
            await self.show_book_content(update, context)
            return
        if "мотивац" in msg:
            await self.show_motivation(update, context)
            return
        if "деньг" in msg or "управл" in msg or "бюджет" in msg:
            await self.show_money(update, context)
            return
        if "меню" in msg or "главное" in msg:
            await self.start(update, context)
            return
        await update.message.reply_text(
            "Напиши на какую тему хочешь узнать: 'Книги', 'Советы', 'FAQ', 'Мотивация', 'Управление деньгами', 'Меню', или нажми на кнопку!",
            reply_markup=get_main_menu_keyboard()
        )

    def setup_handlers(self, application):
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

def main():
    print("🚀 Запуск бота...")
    bot = InvestmentSuperBot()
    application = Application.builder().token(BOT_TOKEN).build()
    bot.setup_handlers(application)
    print("✅ Бот работает! Пиши ему в Telegram /start")
    application.run_polling()

if __name__ == "__main__":
    main()

