import os
import re
import sys
import requests
import subprocess
from dotenv import load_dotenv
from colorama import Fore, Style, init
import pyttsx3 

# --- КОНСТАНТЫ API ---
# Используется стандартный домен Google API
GEMINI_API_HOST = "generativelanguage.googleapis.com"
GEMINI_API_URL = f"https://{GEMINI_API_HOST}/v1beta/models/gemini-2.5-flash:generateContent"
# ---------------------

# Инициализация colorama
init(autoreset=True, wrap=True)

# Загрузка переменной окружения
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print(Fore.RED + "Ошибка: Ключ GEMINI_API_KEY не найден в файле .env")
    sys.exit(1)

# Инициализация TTS-движка
tts_engine = None
try:
    # Убедитесь, что eSpeak-ng (или аналог) установлен
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 170)
    # Поиск русского голоса
    voices = tts_engine.getProperty('voices')
    for voice in voices:
        if 'ru' in voice.id.lower() or 'russian' in voice.id.lower(): 
            tts_engine.setProperty('voice', voice.id)
            break
except Exception:
    # Игнорировать ошибки, если TTS не может быть инициализирован (например, pyttsx3 не находит движка)
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
        # Используем Termux-API TTS (требуется установка Termux:API и Termux:TTS)
        try:
            subprocess.run(["termux-tts-speak", text], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        return
        
    print(Fore.YELLOW + "Функция 'say' недоступна.")


def send_gemini_request(prompt, chat_history):
    """
    Отправляет прямой запрос к Gemini API.
    """
    
    new_history = chat_history + [{"role": "user", "parts": [{"text": prompt}]}]
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY 
    }
    
    data = {
        "contents": new_history,
        "config": {"temperature": 0.7}
    }
    
    try:
        response = requests.post(
            GEMINI_API_URL, 
            headers=headers, 
            json=data,
            verify=True, 
            timeout=30 
        )
        response.raise_for_status()

        json_response = response.json()
        
        # Парсинг ответа
        candidate = json_response.get('candidates', [None])[0]
        if not candidate:
            error_details = json_response.get('error', {}).get('message', 'AI вернул пустой ответ (без видимой ошибки).')
            return f"Ошибка API: {error_details}", chat_history

        ai_response = candidate.get('content', {}).get('parts', [{}])[0].get('text', 'Ошибка: AI вернул пустой текст.')
        
        # Добавляем ответ AI в историю
        new_history.append(candidate['content'])
        
        return ai_response, new_history

    except requests.exceptions.HTTPError as e:
        error_status = e.response.status_code
        error_msg = f"HTTP Ошибка ({error_status}). Проверьте ключ API (401) и убедитесь, что включен VPN/Прокси (403). {e}"
        print(Fore.RED + f"\n{error_msg}")
        return error_msg, chat_history
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Сетевая Ошибка: Не удалось подключиться к Google API. Убедитесь, что включен VPN/Прокси. {e}"
        print(Fore.RED + f"\n{error_msg}")
        return "Не удалось получить ответ от AI (ошибка сети/блокировка).", chat_history
        
    except Exception as e:
        return f"Критическая ошибка: {e}", chat_history

# --- ОСНОВНАЯ ФУНКЦИЯ ---

def main():
    """Основная функция CLI-помощника."""
    chat_history = [] 

    print(Fore.GREEN + Style.BRIGHT + "========================================")
    print(Fore.GREEN + Style.BRIGHT + "  🤖 Gemini CLI-Помощник запущен!   ")
    print(Fore.GREEN + Style.BRIGHT + f"  (Прямое подключение)   ")
    print(Fore.RED + Style.BRIGHT + "  ⚠️ ВНИМАНИЕ: Необходим VPN/Прокси! ⚠️   ")
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