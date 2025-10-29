#!/data/data/com.termux/files/usr/bin/bash

# --- КОНФИГУРАЦИЯ ---
REPO_ZIP_URL="https://github.com/ВАШ_ПОЛЬЗОВАТЕЛЬ/ВАШ_РЕПОЗИТОРИЙ/archive/refs/heads/main.zip" # <<< ЗАМЕНИТЕ ЭТУ ССЫЛКУ!
WORKING_DIR="gemini-cli-assistant"
ZIP_FILE="repo.zip"
UNPACK_DIR=$(basename "$REPO_ZIP_URL" .zip)

echo "==========================================="
echo "  🚀 Установщик Gemini CLI-Помощника"
echo "==========================================="

# 1. Установка базовых пакетов
echo -e "\n[1/4] Установка Termux-пакетов (Python, Git, Wget, Unzip, TTS)..."
pkg update -y
pkg install python git python-pip wget unzip espeak -y

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
if [ -d "$UNPACK_DIR" ]; then
    mv "$UNPACK_DIR"/* .
    rm -r "$UNPACK_DIR"
else
    # Обработка случаев, когда имя папки не соответствует стандарту
    UNPACK_DIR=$(ls -d */ | head -n 1)
    if [ -n "$UNPACK_DIR" ]; then
        mv "$UNPACK_DIR"/* .
        rm -r "$UNPACK_DIR"
    fi
fi

# 4. Установка Python-зависимостей
echo -e "\n[3/4] Установка Python-зависимостей (requests, dotenv, colorama, tts)..."
pip install requests python-dotenv colorama pyttsx3

# 5. Проверка наличия .env
echo -e "\n[4/4] Проверка конфигурационного файла .env..."
if [ ! -f ".env" ]; then
    echo -e "\033[31;1m⚠️ Ошибка: Файл .env не найден в архиве!\033[0m"
    echo "Создайте его вручную с ключом API."
    exit 1
fi

# --- ФИНАЛЬНЫЕ ИНСТРУКЦИИ ---
echo -e "\n==========================================="
echo -e "\033[32;1m✅ Установка завершена!\033[0m"
echo "Чтобы запустить помощника, сначала:"
echo "1. \033[31;1mВключите VPN/Прокси\033[0m, если вы находитесь в России."
echo "2. Перейдите в директорию (если вы не в ней): \033[36;1mcd ~/$WORKING_DIR\033[0m"
echo "3. Запустите скрипт:"
echo -e "\n\033[36;1mpython cli_assistant.py\033[0m"
echo "==========================================="