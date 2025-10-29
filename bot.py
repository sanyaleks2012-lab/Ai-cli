import os
import re
import sys
import subprocess
from dotenv import load_dotenv
from colorama import Fore, Style, init
import pyttsx3 
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Инициализация colorama
init(autoreset=True, wrap=True)

# Загрузка переменной окружения
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print(Fore.RED + "Ошибка: Ключ GEMINI_API_KEY не найден в файле .env")
    sys.exit(1)

# Инициализация клиента Google GenAI
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(Fore.RED + f"Ошибка инициализации клиента Gemini: {e}")
    sys.exit(1)

# Инициализация TTS-движка
tts_engine = None
try:
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 170)
    # Поиск русского голоса
    voices = tts_engine.getProperty('voices')
    for voice in voices:
        if 'ru' in voice.id.lower() or 'russian' in voice.id.lower(): 
            tts_engine.setProperty('voice', voice.id)
            break
except Exception:
    pass

# --- ФУНКЦИИ ---

def speak_text(text):
    """Функция для озвучивания текста (с Termux-API/eSpeak fallback)."""
    if tts_engine:
        print(Fore.MAGENTA + "[ГОВОРЕНИЕ через pyttsx3/eSpeak...]")
        tts_engine.say(text)
        tts_engine.runAndWait()
        return
    
    # Fallback для Termux:API
    if os.path.exists('/data/data/com.termux/files/usr/bin/termux-tts-speak'):
        print(Fore.MAGENTA + "[ГОВОРЕНИЕ через Termux:API...]")
        try:
            subprocess.run(["termux-tts-speak", text], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return
        
    print(Fore.YELLOW + "Функция 'say' недоступна.")


def send_gemini_request(prompt, chat_history):
    """
    Отправляет запрос к Gemini API с использованием genai.Client.
    """
    
    # Создаем новый чат с историей
    # Использование genai.Client.chats.create() позволяет управлять контекстом
    try:
        chat = client.chats.create(
            model="gemini-2.5-flash",
            history=chat_history # Передаем предыдущую историю
        )
        
        # Отправляем новый запрос
        response = chat.send_message(prompt)
        
        # Обновляем историю чата
        new_history = chat.get_history()
        
        return response.text, new_history

    except APIError as e:
        error_msg = f"Ошибка API Gemini (HTTP): Проверьте ключ и VPN/Прокси. Детали: {e}"
        print(Fore.RED + f"\n{error_msg}")
        # Возвращаем старую историю при ошибке
        return error_msg, chat_history
        
    except Exception as e:
        error_msg = f"Критическая сетевая ошибка: Проверьте соединение/VPN. Детали: {e}"
        print(Fore.RED + f"\n{error_msg}")
        return "Не удалось получить ответ от AI.", chat_history

# --- ОСНОВНАЯ ФУНКЦИЯ ---

def main():
    """Основная функция CLI-помощника."""
    # История чата хранится в этом списке
    chat_history = [] 

    print(Fore.GREEN + Style.BRIGHT + "========================================")
    print(Fore.GREEN + Style.BRIGHT + "  🤖 Gemini CLI-Помощник запущен!   ")
    print(Fore.GREEN + Style.BRIGHT + "========================================")
    
    while True:
        try:
            user_input = input(Style.BRIGHT + Fore.BLUE + "you " + Style.RESET_ALL + "> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nВыход...")
            break

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit']:
            print(Fore.GREEN + "До свидания! 👋")
            break

        # Обработка команды 'say'
        say_match = re.match(r'^say\s+"(.+)"$', user_input, re.IGNORECASE)
        if say_match:
            speak_text(say_match.group(1))
            continue
            
        # Отправка запроса к Gemini
        ai_response, chat_history = send_gemini_request(user_input, chat_history)
        
        # Выводим ответ ИИ
        print(Style.BRIGHT + Fore.YELLOW + "AI " + Style.RESET_ALL + f": {ai_response}")

if __name__ == "__main__":
    main()