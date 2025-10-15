import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Настройки для Railway (ключи сразу прописаны, ничего менять не нужно)
BOT_TOKEN = "8203632125:AAFl3OqXf4mKeijmA1-YFmJGP9UMUbCxl0I"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✨ Информационная база (БОЛЬШЕ СЕКЦИЙ):
SALUTATION = "Привет 👋\nЯ бот-помощник по инвестициям!\n\nЯ объясняю самые простые вещи про финансы, инвестиции и личные деньги.\n\nНажимай на кнопки и читай советы!"

WHAT_IS_INVEST = (
    "🟢 Что такое инвестирование?\n"
    "— Это процесс использования денег для покупки активов с целью увеличения их стоимости или получения дохода.\n"
    "Инвестиции могут быть долгосрочными (на годы) и краткосрочными (несколько месяцев).\n"
)

WHY_IMPORTANT = (
    "🌟 Почему важно инвестировать?\n"
    "• Защищаешь деньги от инфляции\n"
    "• Строишь свой капитал и финансовую подушку\n"
    "• Учишься думать о будущем, а не только о сегодня\n"
    "Инвестиции — это способ сделать свою жизнь свободнее благодаря надежным активам."
)

INVEST_TYPES = [
    "• Акции — доля в компании, растёт вместе с бизнесом.",
    "• Облигации — защита капитала, регулярные выплаты процентов.",
    "• ETF — коробочка из акций и облигаций, очень удобно начинающим.",
    "• Валюта — доллары, евро, франки, страховка от падения рубля.",
    "• Недвижимость — физические активы, можно сдавать в аренду.",
    "• Криптовалюта — рискованный актив, только для экспериментаторов.",
    "• Золото — работает как защита капитала в кризис."
]

MAIN_CONCEPTS = [
    "• Диверсификация — распределение денег между разными активами.",
    "• Финансовая цель — зачем и на сколько ты инвестируешь.",
    "• Брокер — сервис для покупки акций и облигаций.",
    "• Портфель — все активы, которыми ты владеешь.",
    "• Риск — возможность потерять часть денег.",
    "• Доходность — сколько ты зарабатываешь в процентах за период.",
    "• Инфляция — рост цен, из-за которого рубли обесцениваются.",
    "• Капитализация — превращение прибыли обратно в новые инвестиции.",
    "• Банковский вклад — самый простой пассивный доход, но ниже чем инвестирование."
]

SAFETY = (
    "🔒 Как не потерять деньги:\n"
    "• Никогда не вкладывай последние деньги!\n"
    "• Проверь лицензии брокера и сервисов.\n"
    "• Не ведись на хайп и обещания огромной прибыли.\n"
    "• Проверяй советы на независимых платформах (ЦБР, investing.com)\n"
    "• Всегда читай отзывы реальных людей и анализируй комиссии."
)

MOTIVATION = (
    "🔥 Мотивация:\n"
    "— Ты сможешь путешествовать, работать где удобно.\n"
    "— Твой капитал растёт даже пока ты спишь.\n"
    "— Деньги работают на тебя!\n"
)

ADVICE = [
    "• Начни с минимальной суммы (1000-3000₽).",
    "• Никогда не инвестируй сразу всё.",
    "• Изучи базу: акции, облигации, ETF (коробочки с бумагами).",
    "• Сохраняй терпение — успех не приходит за месяц.",
    "• Ведите учёт своих трат и результатов.",
    "• Разделяй свои цели на краткосрочные и долгосрочные.",
    "• Читай ценную литературу и статьи по финансам.",
    "• Спросить совет у опытного инвестора — это хорошо!",
]

ERRORS = [
    "• Вкладывать все деньги только в одну акцию.",
    "• Игнорировать комиссии брокера.",
    "• Опираться на плохие советы из чатов.",
    "• Снимать деньги при первом падении — паника = минус.",
    "• Покупать что попало, не имея плана.",
    "• Не иметь финансовой подушки безопасности."
]

FAQ = [
    "1. Как выбрать брокера? — Смотри на отзывы, лицензии и удобство приложения.",
    "2. Какие акции самые надёжные? — Большие госкомпании и фонды.",
    "3. Как начать инвестировать? — Открой счёт, пополни и купи ETF или акцию.",
    "4. Это опасно? — Только если игнорировать диверсификацию и вкладывать последние деньги.",
    "5. Сколько можно заработать? — Надёжно: 7-20% в год, рискованно — больше, но опасней."
]

BOOKS = [
    "• 'Самый богатый человек в Вавилоне' — Дж. Клейсон",
    "• 'Разумный инвестор' — Б. Грэм",
    "• 'Думай и богатей' — Н. Хилл",
    "• 'Психология инвестирования' — К. Ричардс",
]

CURRENCIES = [
    "• USD/RUB: 97.61",
    "• EUR/RUB: 103.44",
]
STOCKS = [
    "• FXRL (ETF Российские акции): 1274.3₽",
    "• FXRB (ETF Российские облигации): 1149.7₽",
    "• Сбербанк: 289.25₽",
    "• Газпром: 146.18₽",
]
CRYPTO = [
    "• Bitcoin: 69000$",
    "• Ethereum: 3740$",
    "• Solana: 32.5$",
]

def get_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📊 Меню", "🟠 Что такое инвест?", "🌟 Почему важно"],
            ["💡 Виды инвестиций", "📖 Основные понятия", "🔒 Безопасность"],
            ["🔥 Мотивация", "🧩 Советы", "🔍 Ошибки"],
            ["📝 FAQ", "📚 Книги"],
            ["💰 Курсы валют", "📈 Акции", "💸 Криптовалюта"],
            ["📊 Статистика"]
        ],
        resize_keyboard=True
    )

class InvestmentInfoBot:
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

    async def start(self, update: Update, context: CallbackContext):
        user = update.effective_user
        self.update_user_stat(user.id, user.first_name)
        await update.message.reply_text(SALUTATION, reply_markup=get_keyboard())

    async def handle_message(self, update: Update, context: CallbackContext):
        user = update.effective_user
        self.update_user_stat(user.id, user.first_name)
        self.increment_questions(user.id)
        msg = update.message.text.strip().lower()
        if "меню" in msg: await update.message.reply_text(SALUTATION, reply_markup=get_keyboard()); return
        if "инвест" in msg: await update.message.reply_text(WHAT_IS_INVEST, reply_markup=get_keyboard()); return
        if "важно" in msg: await update.message.reply_text(WHY_IMPORTANT, reply_markup=get_keyboard()); return
        if "вид" in msg: await update.message.reply_text("💡 Виды инвестиций:\n" + "\n".join(INVEST_TYPES), reply_markup=get_keyboard()); return
        if "понят" in msg: await update.message.reply_text("📖 Основные понятия:\n" + "\n".join(MAIN_CONCEPTS), reply_markup=get_keyboard()); return
        if "безопас" in msg: await update.message.reply_text(SAFETY, reply_markup=get_keyboard()); return
        if "мотивац" in msg: await update.message.reply_text(MOTIVATION, reply_markup=get_keyboard()); return
        if "совет" in msg: await update.message.reply_text("🧩 Советы для новичков:\n" + "\n".join(ADVICE), reply_markup=get_keyboard()); return
        if "ошиб" in msg: await update.message.reply_text("🔍 Ошибки инвестора:\n" + "\n".join(ERRORS), reply_markup=get_keyboard()); return
        if "faq" in msg: await update.message.reply_text("📝 FAQ:\n" + "\n".join(FAQ), reply_markup=get_keyboard()); return
        if "книг" in msg: await update.message.reply_text("📚 Книги:\n" + "\n".join(BOOKS), reply_markup=get_keyboard()); return
        if "валют" in msg: await update.message.reply_text("💰 Курсы валют:\n" + "\n".join(CURRENCIES), reply_markup=get_keyboard()); return
        if "акци" in msg: await update.message.reply_text("📈 Акции и ETF:\n" + "\n".join(STOCKS), reply_markup=get_keyboard()); return
        if "крипт" in msg: await update.message.reply_text("💸 Криптовалюта:\n" + "\n".join(CRYPTO), reply_markup=get_keyboard()); return
        if "стат" in msg:
            con = sqlite3.connect("users.db")
            cur = con.cursor()
            cur.execute("SELECT questions_count, last_visit FROM user_stats WHERE user_id=?", (user.id,))
            row = cur.fetchone()
            con.close()
            if row:
                stats_msg = (
                    f"📊 Ваша статистика:\n"
                    f"Вопросов: {row[0]}\n"
                    f"Последний визит: {row[1]}"
                )
            else:
                stats_msg = "Статистика не найдена."
            await update.message.reply_text(stats_msg, reply_markup=get_keyboard())
            return
        await update.message.reply_text(
            "Напиши на какую тему хочешь узнать: 'Виды', 'Понятия', 'Ошибки', 'FAQ', 'Книги', 'Курсы валюта', 'Акции', 'Крипта', 'Безопасность', 'Советы', 'Мотивация'. Для главного меню — напиши 'Меню'.",
            reply_markup=get_keyboard()
        )

    def setup_handlers(self, application):
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

def main():
    print("🚀 Запуск бота...")
    bot = InvestmentInfoBot()
    application = Application.builder().token(BOT_TOKEN).build()
    bot.setup_handlers(application)
    print("✅ Бот работает! Пиши ему в Telegram /start")
    application.run_polling()

if __name__ == "__main__":
    main()
