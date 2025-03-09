import time
import threading
import telebot
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from telebot import types
from queue import Queue
import traceback

# Список товаров с URL
PRODUCTS = {
    "Маска увлажняющая Moonlight Magic": "https://www.letu.ru/product/soda-maska-dlya-litsa-uvlazhnyayushchaya-moonlight-magic-magicalpower/166500763",
    "Подводка Princess of Lynphea": "https://www.letu.ru/product/soda-pigment-podvodka-dlya-glaz-zhidkaya-princess-of-lynphea-magicalpower/166500791",
    "Подводка Inner Dragon": "https://www.letu.ru/product/soda-pigment-podvodka-dlya-glaz-zhidkaya-inner-dragon-magicalpower/166500792",
    "Набор спонжей Ocean Whirlpool": "https://www.letu.ru/product/soda-nabor-sponzh-dlya-makiyazha-i-podstavka-ocean-whirlpool-magicalpower/166500888",
    "Тушь Cherry Blossom": "https://www.letu.ru/product/soda-tush-dlya-resnits-cherry-blossom-magicalpower/166500800",
    "Палетка теней Beware of Witches": "https://www.letu.ru/product/soda-paletka-tenei-beware-of-witches-magicalpower/166500788",
    "Палетка для лица Heart of Gold": "https://www.letu.ru/product/soda-paletka-dlya-litsa-heart-of-gold-magicalpower/166500778",
    "Палетка для лица Match Made in Heaven": "https://www.letu.ru/product/soda-paletka-dlya-litsa-match-made-in-heaven-magicalpower/166500779",
    "Бальзам для губ Dark Chaos": "https://www.letu.ru/product/soda-balzam-dlya-gub-dark-chaos-magicalpower/166500860",
    "Помада Double Tornado": "https://www.letu.ru/product/soda-pomada-dlya-gub-double-tornado-magicalpower/166500866",
    "Палетка теней Heart of Alfea": "https://www.letu.ru/product/soda-paletka-tenei-heart-of-alfea-magicalpower/166500787",
    "Жидкие тени Domino": "https://www.letu.ru/product/soda-zhidkie-teni-dlya-vek-domino-magicalpower/166500796",
    "Набор спонжей Shooting Star": "https://www.letu.ru/product/soda-nabor-sponzh-dlya-makiyazha-i-podstavka-shooting-star-magicalpower/166500889",
    "Маска охлаждающая Frozen Dreams": "https://www.letu.ru/product/soda-maska-dlya-litsa-ohlazhdayushchaya-frozen-dreams-magicalpower/166500762",
    "Подводка Shining Sun": "https://www.letu.ru/product/soda-pigment-podvodka-dlya-glaz-zhidkaya-shining-sun-magicalpower/166500790",
    "Набор кистей Fairy Secrets": "https://www.letu.ru/product/soda-nabor-kistei-fairy-secrets-magicalpower/166500890",
    "Карандаш для глаз Primordial Void": "https://www.letu.ru/product/soda-karandash-dlya-glaz-primordial-void-magicalpower/166500868",
    "Подарочный набор Sparx Festival": "https://www.letu.ru/product/soda-podarochnyi-nabor-sparx-festival-magicalpower/166500893",
    "Палетка для лица Swirl of Petals": "https://www.letu.ru/product/soda-paletka-dlya-litsa-swirl-of-petals-magicalpower/166500780",
    "Карандаш для глаз Power Awakening": "https://www.letu.ru/product/soda-karandash-dlya-glaz-power-awakening-magicalpower/166500870",
    "Карандаш для глаз Zenith": "https://www.letu.ru/product/soda-karandash-dlya-glaz-zenith-magicalpower/166500872",
    "Жидкий хайлайтер Diamond": "https://www.letu.ru/product/soda-zhidkii-hailaiter-diamond-magicalpower/166500783",
    "Жидкие тени Vertigo": "https://www.letu.ru/product/soda-zhidkie-teni-dlya-vek-vertigo-magicalpower/166500798",
    "Вельветовая помада Hypnotizing": "https://www.letu.ru/product/soda-velvetovaya-pomada-hypnotizing-magicalpower/166500865",
    "Карандаш для глаз World of Ice": "https://www.letu.ru/product/soda-karandash-dlya-glaz-world-of-ice-magicalpower/166500867",
    "Косметичка Great Dragon": "https://www.letu.ru/product/soda-kosmetichka-great-dragon-magicalpower/166500887",
    "Набор кистей Witch Essentials": "https://www.letu.ru/product/soda-nabor-kistei-witch-essentials-magicalpower/166500891",
    "Жидкие тени Andros": "https://www.letu.ru/product/soda-zhidkie-teni-dlya-vek-andros-magicalpower/166500794",
    "Карандаш для глаз Iridescent Blade": "https://www.letu.ru/product/soda-karandash-dlya-glaz-iridescent-blade-magicalpower/166500871",
    "Тушь Ones and Zeros": "https://www.letu.ru/product/sodatush-dlya-resnits-ones-and-zeros-magicalpower/166500777",
    "Глиттер-гель Digital Glitch": "https://www.letu.ru/product/soda-glitter-gel-dlya-litsa-i-tela-digital-glitch-magicalpower/166500784",
    "Глиттер-гель Frozen Wave": "https://www.letu.ru/product/soda-glitter-gel-frozen-wave-magicalpower/166500786",
    "Тушь Raging Storm": "https://www.letu.ru/product/soda-tush-dlya-resnits-raging-storm-magicalpower/166500799",
    "Жидкие тени Solaria": "https://www.letu.ru/product/soda-zhidkie-teni-dlya-vek-solaria-magicalpower/166500795",
    "Палетка теней Magical Dust": "https://www.letu.ru/product/soda-paletka-tenei-magical-dust-magicalpower/166500789",
    "Карандаш для глаз Pure Harmony": "https://www.letu.ru/product/soda-karandash-dlya-glaz-pure-harmony-magicalpower/166500869",
    "Помада Sense of Love": "https://www.letu.ru/product/soda-pomada-dlya-gub-sense-of-love-magicalpower/166500803",
    "Тинт для губ Sunfire": "https://www.letu.ru/product/soda-tint-dlya-gub-sunfire-magicalpower/166500862",
    "Глиттер-гель Harmonic Nebula": "https://www.letu.ru/product/soda-glitter-gel-dlya-litsa-i-tela-harmonic-nebula-magicalpower/166500785",
    "Подарочный набор Sisters Power": "https://www.letu.ru/product/soda-podarochnyi-nabor-sisters-power-gift-set-magicalpower/166500892",
    "Тинт для губ Dance of Dreams": "https://www.letu.ru/product/soda-tint-dlya-gub-dance-of-dreams-magicalpower/166500863",
    "Жидкие тени Melody": "https://www.letu.ru/product/soda-zhidkie-teni-dlya-vek-melody-magicalpower/166500793"
}

# Токен бота и ID чата
TELEGRAM_BOT_TOKEN = "6983722778:AAGcwgMWV20poAkCG78qhM2JEavH5ERTkww"
TELEGRAM_CHAT_ID = "1023121544"
CHECK_INTERVAL = 30
STATUS_INTERVAL = 30
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Отслеживаемые товары и состояние
selected_products = set()
running = True
notified_products = set()
auto_status_running = False
check_queue = Queue()

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36")
    options.add_argument("--disable-images")
    service = Service("./chromedriver.exe")
    return webdriver.Chrome(service=service, options=options)

def check_product_availability(url):
    driver = get_driver()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(
            lambda d: d.find_elements(By.XPATH, "//button[contains(., 'В корзину') or @data-action='add-to-cart']") or
                      d.find_elements(By.XPATH, "//*[contains(text(), 'Нет в наличии') or contains(text(), 'Товар отсутствует')]")
        )
        for _ in range(2):  # Повторная попытка при stale element
            try:
                buttons = driver.find_elements(By.XPATH, "//button[contains(., 'В корзину') or @data-action='add-to-cart']")
                if buttons:
                    button = buttons[0]
                    if button.is_enabled() and "disabled" not in button.get_attribute("class"):
                        print(f"Товар {url} в наличии: кнопка 'В корзину' активна")
                        return True
                    else:
                        print(f"Товар {url} отсутствует: кнопка 'В корзину' отключена")
                        return False
                if any("Нет в наличии" in elem.text or "Товар отсутствует" in elem.text for elem in driver.find_elements(By.XPATH, "//*")):
                    print(f"Товар {url} отсутствует: найден текст 'Нет в наличии'")
                    return False
                print(f"Товар {url} отсутствует: не найдено ни кнопки, ни текста")
                return False
            except StaleElementReferenceException:
                print(f"Повторная попытка проверки {url} из-за stale element")
                time.sleep(1)
        return False
    except TimeoutException:
        print(f"Ошибка при проверке товара {url}: Таймаут ожидания элемента")
        return False
    except Exception as e:
        print(f"Ошибка при проверке товара {url}: {str(e)}")
        with open(f"debug_{url.split('/')[-3]}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        return False
    finally:
        driver.quit()

def check_selected_products():
    status = {}
    print("Проверка статуса выбранных товаров...")
    for name in selected_products:
        status[name] = check_product_availability(PRODUCTS[name])
    print("Проверка статуса завершена.")
    return status

def send_status():
    if not selected_products:
        try:
            bot.send_message(TELEGRAM_CHAT_ID, "Вы не выбрали товары. Используйте /select для выбора.")
            print("Отправлено сообщение: нет выбранных товаров")
        except Exception as e:
            print(f"Ошибка отправки статуса: {str(e)}")
        return
    status = check_selected_products()
    response = "Статус товаров:\n" + "\n".join(
        [f"{name}: {'В наличии' if available else 'Нет в наличии'}" for name, available in status.items()]
    )
    try:
        bot.send_message(TELEGRAM_CHAT_ID, response)
        print("Статус отправлен: ", response)
    except Exception as e:
        print(f"Ошибка отправки статуса: {str(e)}")

def background_check_thread():
    while running:
        try:
            if not check_queue.empty():
                print("Обрабатываю задачу из очереди...")
                available_products = check_selected_products()
                in_stock = [name for name, available in available_products.items() if available and name not in notified_products]
                if in_stock:
                    message = "Товары в наличии:\n" + "\n".join(in_stock) + "\nПерейдите в корзину: https://www.letu.ru/cart"
                    bot.send_message(TELEGRAM_CHAT_ID, message)
                    print("Уведомление отправлено: ", message)
                    with threading.Lock():
                        notified_products.update(in_stock)
                else:
                    bot.send_message(TELEGRAM_CHAT_ID, "Пока ничего из выбранного нет в наличии.")
                    print("Отправлено сообщение: ничего в наличии нет")
                check_queue.get()
                check_queue.task_done()
            elif selected_products:
                print("Проверяю наличие в фоновом режиме...")
                available_products = check_selected_products()
                in_stock = [name for name, available in available_products.items() if available and name not in notified_products]
                if in_stock:
                    message = "Товары в наличии:\n" + "\n".join(in_stock) + "\nПерейдите в корзину: https://www.letu.ru/cart"
                    bot.send_message(TELEGRAM_CHAT_ID, message)
                    print("Уведомление отправлено: ", message)
                    with threading.Lock():
                        notified_products.update(in_stock)
            else:
                print("Ожидаю выбора товаров через /select...")
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            print(f"Ошибка в фоновом потоке: {str(e)}\nТрассировка: {traceback.format_exc()}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global running
    running = True
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_stop = types.KeyboardButton("Стоп")
    btn_auto_status = types.KeyboardButton("Автостатус")
    markup.add(btn_stop, btn_auto_status)
    bot.reply_to(message, "Привет! Выбери товары с помощью /select или проверь статус /status.", reply_markup=markup)

@bot.message_handler(commands=['select'])
def select_products(message):
    markup = types.InlineKeyboardMarkup()
    for name in PRODUCTS.keys():
        markup.add(types.InlineKeyboardButton(name, callback_data=f"select_{name}"))
    bot.send_message(message.chat.id, "Выбери товары:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("select_"))
def callback_select(call):
    product_name = call.data.replace("select_", "")
    if product_name in selected_products:
        selected_products.remove(product_name)
        bot.send_message(TELEGRAM_CHAT_ID, f"Убрано: {product_name}")
    else:
        selected_products.add(product_name)
        bot.send_message(TELEGRAM_CHAT_ID, f"Добавлено: {product_name}")
    bot.edit_message_text(f"Выбранные товары: {', '.join(selected_products) if selected_products else 'Пока нет'}",
                          chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=call.message.reply_markup)
    if selected_products:
        print(f"Добавляю задачу в очередь для проверки {selected_products}")
        check_queue.put(True)

@bot.message_handler(commands=['status'])
def check_status(message):
    send_status()

@bot.message_handler(func=lambda message: message.text == "Стоп")
def stop_notifications(message):
    global running
    running = False
    bot.reply_to(message, "Проверка остановлена. Для возобновления используйте /start.")

@bot.message_handler(func=lambda message: message.text == "Автостатус")
def toggle_auto_status(message):
    global auto_status_running
    auto_status_running = not auto_status_running
    if auto_status_running:
        bot.reply_to(message, "Автоматическая отправка статуса каждые 30 секунд включена. Нажми 'Автостатус' еще раз, чтобы отключить.")
        threading.Thread(target=auto_status_thread, daemon=True).start()
    else:
        bot.reply_to(message, "Автоматическая отправка статуса отключена.")

def auto_status_thread():
    while auto_status_running:
        send_status()
        time.sleep(STATUS_INTERVAL)

if __name__ == "__main__":
    print("Бот запущен!")
    threading.Thread(target=background_check_thread, daemon=True).start()
    bot.polling(none_stop=True)