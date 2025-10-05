import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from selenium.webdriver.common.action_chains import ActionChains

# Настройки
TIKTOK_LOGIN = "mc_final"
TIKTOK_PASSWORD = "sosiska173."
CLIPS_FOLDER = "subtitled_clips"  # Папка с готовыми клипами
COOKIES_FILE = "tiktok_cookies.json"  # Файл для сохранения cookies
HASHTAGS = ["#видео", "#тикток", "#развлечения", "#пример", "#клип"]  # Список хештегов
CAPTIONS = [
    "Смотрите новый клип!",
    "Не пропустите это видео!",
    "Вот что мы приготовили для вас сегодня!",
]  # Список подписей

def get_random_hashtags(num_hashtags=3):
    """
    Возвращает строку со случайными хештегами.
    """
    return " ".join(random.sample(HASHTAGS, num_hashtags))

def get_random_caption():
    """
    Возвращает случайную подпись.
    """
    return random.choice(CAPTIONS)

def random_sleep(min_seconds=1, max_seconds=5):
    """
    Случайная пауза между действиями.
    """
    time.sleep(random.randint(min_seconds, max_seconds))

def save_cookies(driver, filename):
    """
    Сохраняет cookies в файл.
    """
    cookies = driver.get_cookies()
    with open(filename, "w") as file:
        json.dump(cookies, file)
    print(f"Cookies сохранены в {filename}")

def load_cookies(driver, filename):
    """
    Загружает cookies из файла.
    """
    if not os.path.exists(filename):
        return False

    with open(filename, "r") as file:
        cookies = json.load(file)
    for cookie in cookies:
        driver.add_cookie(cookie)
    print(f"Cookies загружены из {filename}")
    return True

def close_cookie_banner(driver):
    """
    Закрывает баннер cookie, если он есть.
    """
    try:
        # Ищем кнопку закрытия баннера cookie
        cookie_banner = driver.find_element(By.TAG_NAME, "tiktok-cookie-banner")
        if cookie_banner:
            # Нажимаем кнопку "Принять" или "Закрыть"
            accept_button = cookie_banner.find_element(By.XPATH, ".//button[contains(text(), 'Принять')]")
            if accept_button:
                accept_button.click()
                print("Баннер cookie закрыт.")
                random_sleep()
    except Exception as e:
        print(f"Баннер cookie не найден или не удалось закрыть: {e}")

def login_to_tiktok(driver):
    """
    Вход в аккаунт TikTok.
    """
    print("Вход в аккаунт...")
    driver.get("https://www.tiktok.com/login/phone-or-email/email")  # Переход на страницу для авторизации через email
    random_sleep()

    # Закрываем баннер cookie, если он есть
    close_cookie_banner(driver)

    # Ввод логина
    login_input = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/div[1]/input')
    login_input.send_keys(TIKTOK_LOGIN)
    random_sleep()

    # Ввод пароля
    password_input = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/div[2]/div/input')
    password_input.send_keys(TIKTOK_PASSWORD)
    random_sleep()

    # Нажатие кнопки входа
    login_button = driver.find_element(By.XPATH, '//*[@id="loginContainer"]/div[1]/form/button')
    actions = ActionChains(driver)
    actions.move_to_element(login_button).click().perform()  # Клик с прокруткой
    random_sleep()

    # Сохраняем cookies после успешного входа
    save_cookies(driver, COOKIES_FILE)

def upload_to_tiktok(video_path):
    """
    Загружает видео в TikTok.
    """
    # Настройки для Chromium
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")  # Важно для Raspberry Pi
    chrome_options.add_argument("--disable-dev-shm-usage")  # Важно для Raspberry Pi
    chrome_options.add_argument("--disable-gpu")  # Отключение GPU
    chrome_options.add_argument("--remote-debugging-port=9222")  # Указываем порт для DevTools
    chrome_options.add_argument("--disable-software-rasterizer")  # Отключаем софтверный рендеринг
    chrome_options.binary_location = "/usr/bin/chromium-browser"  # Указываем путь к Chromium

    # Укажите путь к ChromeDriver
    service = Service("/usr/bin/chromedriver")
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Применяем stealth
    stealth(
        driver,
        languages=["ru-RU", "ru"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
    )

    try:
        # Открываем TikTok
        login_to_tiktok(driver)
        random_sleep()

        # Загружаем cookies, если они есть
        # if not load_cookies(driver, COOKIES_FILE):

        # сли cookies нет, выполняем вход
            

        # Переходим на страницу загрузки
        driver.get("https://www.tiktok.com/upload?lang=ru-RU")
        random_sleep()

        # Загрузка видео
        print("Загрузка видео...")
        upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
        upload_input.send_keys(video_path)
        random_sleep()

        # Добавление подписи и хештегов
        caption = get_random_caption()
        hashtags = get_random_hashtags()
        caption_field = driver.find_element(By.XPATH, "//textarea[@placeholder='Добавьте подпись...']")
        caption_field.send_keys(f"{caption} {hashtags}")
        random_sleep()

        # Публикация
        print("Публикация видео...")
        driver.find_element(By.XPATH, "//button[contains(text(), 'Опубликовать')]").click()
        random_sleep()

    finally:
        # Браузер не закрывается автоматически
        pass

def get_next_clip(clips_folder):
    """
    Возвращает путь к следующему клипу для публикации.
    """
    clips = [f for f in os.listdir(clips_folder) if f.endswith(".mp4")]
    if not clips:
        return None
    return os.path.join(clips_folder, clips[0])

def main():
    """
    Основная функция для публикации клипа.
    """
    # Получаем следующий клип
    clip_path = get_next_clip(CLIPS_FOLDER)
    if not clip_path:
        print("Нет клипов для публикации.")
        return

    # Загружаем клип в TikTok
    print(f"Публикация клипа: {clip_path}")
    upload_to_tiktok(clip_path)

    # Удаляем загруженное видео
    os.remove(clip_path)
    print(f"Клип удален: {clip_path}")

if __name__ == "__main__":
    main()
