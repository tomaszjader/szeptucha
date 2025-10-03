"""
Moduł do przetwarzania i wklejania rozpoznanego tekstu
"""
import time
import threading
import pyperclip
import win32gui
from typing import Optional
from pynput import keyboard as pynput_keyboard


class TextProcessor:
    """Klasa odpowiedzialna za przetwarzanie i wklejanie rozpoznanego tekstu"""
    
    def __init__(self):
        """Inicjalizuje procesor tekstu"""
        pass
    
    def process_recognized_text(self, text: str):
        """
        Przetwarza rozpoznany tekst - wyświetla go i wkleja jeśli to możliwe
        
        Args:
            text: Rozpoznany tekst do przetworzenia
        """
        if not text or not text.strip():
            print("❌ Brak tekstu do przetworzenia")
            return
            
        print(f"\n📝 ROZPOZNANY TEKST:")
        print(f"'{text}'")
        print("-" * 50)
        
        # Sprawdź czy jakieś okno jest aktywne i w trybie pisania
        if self.is_text_input_active():
            print("✍️ Wykryto aktywne pole tekstowe - wklejam tekst...")
            self.paste_text(text)
        else:
            print("💬 Tekst wyświetlony w terminalu")
    
    def paste_text(self, text: str):
        """
        Wkleja tekst do aktywnego pola tekstowego
        
        Args:
            text: Tekst do wklejenia
        """
        try:
            # Kopiuj do schowka
            pyperclip.copy(text)
            time.sleep(0.1)  # Krótka pauza
            
            # Wklejanie w osobnym wątku, aby uniknąć blokowania
            def _paste_async():
                try:
                    controller = pynput_keyboard.Controller()
                    controller.press(pynput_keyboard.Key.ctrl)
                    controller.press('v')
                    controller.release('v')
                    controller.release(pynput_keyboard.Key.ctrl)
                except Exception as e:
                    print(f"⚠️ Błąd podczas wklejania (pynput): {e}")
                    # Fallback do biblioteki keyboard, jeśli dostępna
                    try:
                        import keyboard as kb
                        kb.send('ctrl+v')
                    except Exception as e2:
                        print(f"⚠️ Błąd podczas wklejania (keyboard): {e2}")
            
            threading.Thread(target=_paste_async, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Błąd podczas kopiowania do schowka: {e}")
    
    def is_text_input_active(self) -> bool:
        """
        Sprawdza czy aktywne jest pole tekstowe
        
        Returns:
            bool: True jeśli aktywne pole tekstowe zostało wykryte, False w przeciwnym razie
        """
        try:
            # Pobierz informacje o aktywnym oknie
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return False
                
            class_name = win32gui.GetClassName(hwnd)
            window_text = win32gui.GetWindowText(hwnd)
            
            # Lista klas okien, które prawdopodobnie mają pola tekstowe
            text_input_classes = [
                'Edit', 'RichEdit', 'RichEdit20A', 'RichEdit20W',
                'Notepad', 'WordPadClass', 'OpusApp',  # Word
                'Chrome_WidgetWin_1', 'MozillaWindowClass',  # Przeglądarki
                'Vim', 'ConsoleWindowClass',  # Edytory tekstu
                'SciTEWindow', 'Notepad++',  # Inne edytory
                'ThunderRT6TextBox', 'TMemo'  # Inne kontrolki tekstowe
            ]
            
            # Sprawdź czy nazwa klasy sugeruje pole tekstowe
            for text_class in text_input_classes:
                if text_class.lower() in class_name.lower():
                    return True
            
            # Sprawdź czy tytuł okna sugeruje edytor tekstu
            text_indicators = [
                'notepad', 'word', 'editor', 'code', 'text', 'write',
                'document', 'edit', 'vim', 'emacs', 'sublime', 'vscode',
                'atom', 'brackets', 'gedit', 'nano'
            ]
            
            window_text_lower = window_text.lower()
            for indicator in text_indicators:
                if indicator in window_text_lower:
                    return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ Błąd podczas sprawdzania aktywnego okna: {e}")
            return False
    
    def get_active_window_info(self) -> Optional[dict]:
        """
        Pobiera informacje o aktywnym oknie
        
        Returns:
            Optional[dict]: Słownik z informacjami o oknie lub None w przypadku błędu
        """
        try:
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                return None
                
            return {
                'handle': hwnd,
                'class_name': win32gui.GetClassName(hwnd),
                'window_text': win32gui.GetWindowText(hwnd),
                'is_text_input': self.is_text_input_active()
            }
            
        except Exception as e:
            print(f"⚠️ Błąd podczas pobierania informacji o oknie: {e}")
            return None
    
    def type_text_directly(self, text: str):
        """
        Wpisuje tekst bezpośrednio (alternatywa dla wklejania)
        
        Args:
            text: Tekst do wpisania
        """
        try:
            def _type_async():
                try:
                    controller = pynput_keyboard.Controller()
                    # Małe opóźnienie przed rozpoczęciem pisania
                    time.sleep(0.1)
                    controller.type(text)
                except Exception as e:
                    print(f"⚠️ Błąd podczas pisania tekstu: {e}")
            
            threading.Thread(target=_type_async, daemon=True).start()
            
        except Exception as e:
            print(f"❌ Błąd podczas inicjalizacji pisania tekstu: {e}")


class ClipboardManager:
    """Klasa do zarządzania schowkiem"""
    
    @staticmethod
    def copy_to_clipboard(text: str) -> bool:
        """
        Kopiuje tekst do schowka
        
        Args:
            text: Tekst do skopiowania
            
        Returns:
            bool: True jeśli operacja się powiodła, False w przeciwnym razie
        """
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"❌ Błąd podczas kopiowania do schowka: {e}")
            return False
    
    @staticmethod
    def get_from_clipboard() -> Optional[str]:
        """
        Pobiera tekst ze schowka
        
        Returns:
            Optional[str]: Tekst ze schowka lub None w przypadku błędu
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"❌ Błąd podczas pobierania ze schowka: {e}")
            return None