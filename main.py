import sys
import logging
import pytesseract
from PIL import Image, ImageGrab
from deep_translator import GoogleTranslator
from win10toast_click import ToastNotifier
import pyperclip
import keyboard

# ===================== НАСТРОЙКА ЛОГИРОВАНИЯ =====================
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ===================== КОНФИГУРАЦИЯ =====================
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Путь к Tesseract
HOTKEY = "ctrl+shift+alt+o"  # Горячая клавиша
TRANSLATE_TO_LANG = "ru"  # Язык перевода

# ===================== ИНИЦИАЛИЗАЦИЯ =====================
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
toaster = ToastNotifier()

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================
#def hide_console():
 #   """Скрыть консольное окно (для Windows)"""
  #  if sys.platform == "win32":
   #     import win32gui
    #    import win32con
     #   win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_HIDE)

def log_error(error: str):
    """Запись ошибки в лог"""
    logging.error(error)
    print(f"Произошла ошибка: {error}")  # Для отладки при запуске из консоли

def get_clipboard_image():
    """Получение изображения из буфера обмена"""
    try:
        img = ImageGrab.grabclipboard()
        return img.convert("RGB") if img else None
    except Exception as e:
        log_error(f"Ошибка при получении изображения: {str(e)}")
        return None

# ===================== ОСНОВНОЙ ФУНКЦИОНАЛ =====================
def recognize_text(image: Image) -> str:
    """Распознавание текста с изображения"""
    try:
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        log_error(f"Ошибка распознавания текста: {str(e)}")
        return ""

def translate_text(text: str) -> str:
    """Перевод текста"""
    try:
        return GoogleTranslator(source='auto', target=TRANSLATE_TO_LANG).translate(text)
    except Exception as e:
        log_error(f"Ошибка перевода: {str(e)}")
        return ""

def handle_notification(translated_text: str):
    """Обработка уведомления и буфера обмена"""
    def copy_to_clipboard():
        try:
            pyperclip.copy(translated_text)
        except Exception as e:
            log_error(f"Ошибка копирования: {str(e)}")

    toaster.show_toast(
        "Перевод текста",
        translated_text[:200] + "..." if len(translated_text) > 200 else translated_text,
        duration=10,
        threaded=True,
        callback_on_click=lambda: copy_to_clipboard()
    )

# ===================== ГЛАВНЫЙ ЦИКЛ =====================
def main_process():
    """Основной процесс обработки данных"""
    try:
        if (image := get_clipboard_image()) is None:
            return handle_notification("В буфере нет изображения!")

        if not (text := recognize_text(image)):
            return handle_notification("Текст не распознан!")

        if not (translated := translate_text(text)):
            return handle_notification("Ошибка перевода!")

        handle_notification(translated)

    except Exception as e:
        log_error(f"Критическая ошибка: {str(e)}")

# ===================== ЗАПУСК ПРИЛОЖЕНИЯ =====================
if __name__ == "__main__":
    #hide_console()
    
    # Информация для отладки
    print(f"Приложение запущено. Используйте {HOTKEY} для активации.")
    print("Логи ошибок сохраняются в app.log")

    # Регистрация горячей клавиши
    keyboard.add_hotkey(HOTKEY, main_process)
    
    # Бесконечное ожидание
    try:
        keyboard.wait()
    except KeyboardInterrupt:
        print("Приложение завершено")
    except Exception as e:
        log_error(f"Ошибка в главном цикле: {str(e)}")