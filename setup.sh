#!/data/data/com.termux/files/usr/bin/bash

# --- КОНФИГУРАЦИЯ ---
REPO_ZIP_URL="https://github.com/sanyaleks2012-lab/Ai-cli/archive/refs/heads/main.zip"
WORKING_DIR="gemini-cli-assistant"
ZIP_FILE="repo.zip"
# Имя директории после распаковки Ai-cli-main/
UNPACK_SUBDIR="Ai-cli-main" 

echo "==========================================="
echo "  🚀 Установщик Gemini CLI-Помощника"
echo "==========================================="

# 1. Установка базовых пакетов и компиляторов
# Включает: Python, Git, Wget, Unzip, eSpeak, Rust, CMake, Make, Clang
echo -e "\n[1/4] Установка Termux-пакетов (Python, Rust, CMake, Make, TTS)..."
pkg update -y
pkg install python git wget unzip espeak clang rust cmake make -y

# 2. Создание и переход в рабочую директорию
echo "Создание рабочей директории $WORKING_DIR..."
if [ -d "$WORKING_DIR" ]; then
    echo "Директория $WORKING_DIR уже существует. Удаляем старую версию..."
    rm -rf "$WORKING_DIR"
fi
mkdir "$WORKING_DIR"
cd "$WORKING_DIR"

# 3. Скачивание и распаковка архива
echo -e "\n[2/4] Скачивание архива репозитория с GitHub..."
wget -O "$ZIP_FILE" "$REPO_ZIP_URL"

echo "Распаковка файлов..."
unzip -q "$ZIP_FILE"
rm "$ZIP_FILE"

# Перемещение файлов из поддиректории в основную
echo "Перемещение файлов в корневую директорию..."
if [ -d "$UNPACK_SUBDIR" ]; then
    mv "$UNPACK_SUBDIR"/* .
    rm -r "$UNPACK_SUBDIR"
else
    echo -e "\033[31;1m⚠️ Внимание: Не удалось найти поддиректорию $UNPACK_SUBDIR. Проверьте структуру архива.\033[0m"
    exit 1
fi

# 4. Установка Python-пакет-менеджера uv
echo -e "\n[3/4] Установка менеджера пакетов uv..."
pip install uv

# 5. Установка Python-зависимостей с помощью uv
# Включает pydantic, requests, dotenv, colorama, pyttsx3
echo -e "\n[4/4] Установка Python-зависимостей (requests, dotenv, pydantic и др.) с помощью uv..."
# Убедитесь, что в этом списке указаны все ваши зависимости!
uv pip install requests python-dotenv colorama pyttsx3 pydantic

# 6. Проверка наличия .env
echo -e "\nПроверка конфигурационного файла .env..."
if [ ! -f ".env" ]; then
    echo -e "\033[31;1m⚠️ КРИТИЧЕСКАЯ ОШИБКА: Файл .env с вашим ключом API не найден в репозитории!\033[0m"
    echo "Пожалуйста, убедитесь, что вы загрузили .env в архив GitHub."
    exit 1
fi

# --- ФИНАЛЬНЫЕ ИНСТРУКЦИИ ---
echo -e "\n==========================================="
echo -e "\033[32;1m✅ Установка завершена!\033[0m"
echo "Чтобы запустить помощника, выполните следующие шаги:"
echo "1. \033[31;1mВключите VPN/Прокси\033[0m (если вы находитесь в России)."
echo "2. Запустите скрипт из текущей директории:"
echo -e "\n\033[36;1mpython cli_assistant.py\033[0m"
echo "==========================================="