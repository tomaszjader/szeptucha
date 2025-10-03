"""
Moduł do zarządzania skrótami klawiszowymi
"""
import time
from typing import Callable, Optional
from pynput import keyboard as pynput_keyboard
from config import Config


class HotkeyManager:
    """Klasa odpowiedzialna za zarządzanie globalnymi skrótami klawiszowymi"""
    
    def __init__(self, callback: Callable[[], None]):
        """
        Inicjalizuje menedżer skrótów klawiszowych
        
        Args:
            callback: Funkcja wywoływana po naciśnięciu skrótu
        """
        self.callback = callback
        self.hotkey_listener: Optional[pynput_keyboard.GlobalHotKeys] = None
        self.last_toggle_ts = 0.0  # Debounce dla skrótu
        
    def setup_hotkey(self, hotkey_combination: str = None) -> bool:
        """
        Konfiguruje globalny skrót klawiszowy
        
        Args:
            hotkey_combination: Kombinacja klawiszy (domyślnie z config)
            
        Returns:
            bool: True jeśli skrót został skonfigurowany, False w przeciwnym razie
        """
        if hotkey_combination is None:
            hotkey_combination = Config.HOTKEY_COMBINATION
            
        try:
            # Zatrzymaj poprzedni listener jeśli istnieje
            self.stop_hotkey()
            
            # Utwórz nowy listener
            self.hotkey_listener = pynput_keyboard.GlobalHotKeys({
                hotkey_combination: self._on_hotkey
            })
            
            self.hotkey_listener.start()
            print(f"🔥 Skrót klawiszowy {hotkey_combination} został aktywowany!")
            return True
            
        except Exception as e:
            print(f"❌ Błąd podczas konfiguracji skrótu klawiszowego: {e}")
            return False
    
    def _on_hotkey(self):
        """Obsługuje naciśnięcie skrótu klawiszowego z debounce"""
        # Debounce, żeby uniknąć podwójnych wywołań
        now = time.time()
        if (now - self.last_toggle_ts) < Config.HOTKEY_DEBOUNCE_TIME:
            return
            
        self.last_toggle_ts = now
        
        try:
            self.callback()
        except Exception as e:
            print(f"❌ Błąd podczas obsługi skrótu klawiszowego: {e}")
    
    def stop_hotkey(self):
        """Zatrzymuje nasłuchiwanie skrótów klawiszowych"""
        if self.hotkey_listener:
            try:
                self.hotkey_listener.stop()
                self.hotkey_listener = None
                print("⏹️ Skrót klawiszowy został wyłączony")
            except Exception as e:
                print(f"⚠️ Błąd podczas zatrzymywania skrótu: {e}")
    
    def is_active(self) -> bool:
        """
        Sprawdza czy skrót klawiszowy jest aktywny
        
        Returns:
            bool: True jeśli skrót jest aktywny, False w przeciwnym razie
        """
        return self.hotkey_listener is not None
    
    def change_hotkey(self, new_hotkey_combination: str) -> bool:
        """
        Zmienia kombinację skrótu klawiszowego
        
        Args:
            new_hotkey_combination: Nowa kombinacja klawiszy
            
        Returns:
            bool: True jeśli zmiana się powiodła, False w przeciwnym razie
        """
        return self.setup_hotkey(new_hotkey_combination)
    
    def __del__(self):
        """Destruktor - zatrzymuje listener"""
        self.stop_hotkey()


class HotkeyValidator:
    """Klasa do walidacji kombinacji skrótów klawiszowych"""
    
    @staticmethod
    def validate_hotkey_combination(combination: str) -> bool:
        """
        Waliduje kombinację skrótu klawiszowego
        
        Args:
            combination: Kombinacja do walidacji (np. '<ctrl>+<alt>')
            
        Returns:
            bool: True jeśli kombinacja jest poprawna, False w przeciwnym razie
        """
        try:
            # Sprawdź czy kombinacja zawiera poprawne modyfikatory
            valid_modifiers = ['<ctrl>', '<alt>', '<shift>', '<cmd>']
            valid_keys = ['<space>', '<enter>', '<tab>', '<esc>']
            
            # Dodaj litery i cyfry
            for i in range(26):
                valid_keys.append(chr(ord('a') + i))
            for i in range(10):
                valid_keys.append(str(i))
            
            # Podziel kombinację na części
            parts = combination.lower().split('+')
            
            # Sprawdź czy wszystkie części są poprawne
            for part in parts:
                part = part.strip()
                if part not in valid_modifiers and part not in valid_keys:
                    # Sprawdź czy to pojedyncza litera/cyfra bez nawiasów
                    if len(part) == 1 and (part.isalnum() or part in '!@#$%^&*()'):
                        continue
                    return False
            
            return len(parts) >= 2  # Wymagaj przynajmniej 2 klawiszy
            
        except Exception:
            return False
    
    @staticmethod
    def get_common_hotkey_combinations():
        """
        Zwraca listę popularnych kombinacji skrótów
        
        Returns:
            dict: Słownik z kombinacjami i ich opisami
        """
        return {
            '<ctrl>+<alt>': 'Ctrl + Alt',
            '<ctrl>+<shift>': 'Ctrl + Shift',
            '<alt>+<shift>': 'Alt + Shift',
            '<ctrl>+<alt>+r': 'Ctrl + Alt + R',
            '<ctrl>+<alt>+v': 'Ctrl + Alt + V',
            '<ctrl>+<shift>+r': 'Ctrl + Shift + R',
            '<alt>+<space>': 'Alt + Spacja'
        }