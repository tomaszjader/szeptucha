"""
Moduł okna nagrywania z wizualizacją audio
"""
import tkinter as tk
import threading
import queue
import math
import numpy as np
from collections import deque
from config import Config


class RecordingWindow:
    """Klasa okna nagrywania z wizualizacją fali dźwiękowej"""
    
    def __init__(self, root: tk.Tk):
        """
        Inicjalizuje okno nagrywania
        
        Args:
            root: Główne okno Tkinter
        """
        # Główny root Tk musi działać w głównym wątku
        self.root = root
        self.window = None
        self.canvas = None
        self.visible = False
        self.animation_frame = 0
        self.audio_level = 0.0  # Poziom dźwięku (0.0 - 1.0)
        self.audio_history = deque(maxlen=Config.AUDIO_HISTORY_SIZE)  # Historia poziomów dźwięku
        self.width, self.height = Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT

        # Kolejka do komunikacji między wątkami (show/hide z innych wątków)
        self.command_queue = queue.Queue()
        # Blokada dla bezpiecznego dostępu do danych audio
        self.data_lock = threading.Lock()

    def start(self):
        """Uruchamia pętlę przetwarzania poleceń i animacji (wątku głównego Tk)."""
        def tick():
            # Przetwórz oczekujące polecenia (show/hide) z innych wątków
            try:
                while True:
                    cmd = self.command_queue.get_nowait()
                    if cmd == 'show':
                        self._open_window()
                    elif cmd == 'hide':
                        self._close_window()
            except queue.Empty:
                pass

            # Aktualizuj animację jeśli okno jest widoczne
            if self.visible and self.window and self.canvas:
                try:
                    self._draw_wave_visualization(self.width, self.height)
                    self.animation_frame += Config.ANIMATION_SPEED
                except Exception as e:
                    print(f"⚠️ Błąd animacji: {e}")

            # Zaplanuj następną aktualizację
            self.root.after(50, tick)  # 20 FPS

        # Uruchom pętlę
        tick()

    def show(self):
        """Pokazuje okno nagrywania (bezpieczne wywołanie z innych wątków)"""
        try:
            self.command_queue.put('show')
        except Exception as e:
            print(f"⚠️ Błąd podczas pokazywania okna: {e}")

    def hide(self):
        """Ukrywa okno nagrywania (bezpieczne wywołanie z innych wątków)"""
        try:
            self.command_queue.put('hide')
        except Exception as e:
            print(f"⚠️ Błąd podczas ukrywania okna: {e}")

    def _open_window(self):
        """Otwiera okno nagrywania (tylko w głównym wątku Tk)"""
        if self.visible:
            return

        try:
            self.window = tk.Toplevel(self.root)
            self.window.title("🎤 Nagrywanie...")
            self.window.geometry(f"{self.width}x{self.height}")
            
            # Ustaw okno zawsze na wierzchu i bez ramki
            self.window.attributes('-topmost', True)
            self.window.overrideredirect(True)
            
            # Wyśrodkuj okno na ekranie
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - self.width) // 2
            y = (screen_height - self.height) // 2
            self.window.geometry(f"{self.width}x{self.height}+{x}+{y}")
            
            # Utwórz canvas do rysowania wizualizacji
            self.canvas = tk.Canvas(self.window, width=self.width, height=self.height, bg='black')
            self.canvas.pack()
            
            self.visible = True
            
        except Exception as e:
            print(f"❌ Błąd podczas otwierania okna nagrywania: {e}")
            self.visible = False

    def _close_window(self):
        """Zamyka okno nagrywania (tylko w głównym wątku Tk)"""
        if not self.visible:
            return
            
        try:
            if self.window:
                self.window.destroy()
                self.window = None
                self.canvas = None
            self.visible = False
        except Exception as e:
            print(f"⚠️ Błąd podczas zamykania okna: {e}")

    def _draw_wave_visualization(self, width, height):
        """
        Rysuje wizualizację fali dźwiękowej
        
        Args:
            width: Szerokość canvas
            height: Wysokość canvas
        """
        if not self.canvas:
            return
            
        try:
            # Wyczyść canvas
            self.canvas.delete("all")
            
            # Pobierz dane audio w bezpieczny sposób
            with self.data_lock:
                audio_data = list(self.audio_history)
                current_level = self.audio_level
            
            # Rysuj tło z gradientem
            self._draw_gradient_background(width, height)
            
            # Rysuj główny wskaźnik poziomu
            self._draw_level_indicator(width, height, current_level)
            
            # Rysuj falę dźwiękową
            if audio_data:
                self._draw_waveform(width, height, audio_data)
            
            # Rysuj tekst
            self.canvas.create_text(
                width // 2, height - 20,
                text="🎤 Nagrywanie w toku...",
                fill="white",
                font=("Arial", 10, "bold")
            )
            
        except Exception as e:
            print(f"⚠️ Błąd podczas rysowania wizualizacji: {e}")

    def _draw_gradient_background(self, width, height):
        """Rysuje gradient w tle"""
        try:
            # Prosty gradient przez prostokąty
            for i in range(height):
                intensity = int(20 + (i / height) * 40)
                color = f"#{intensity:02x}{intensity//2:02x}{intensity//4:02x}"
                self.canvas.create_line(0, i, width, i, fill=color)
        except Exception:
            # Fallback - jednolite tło
            self.canvas.create_rectangle(0, 0, width, height, fill="#1a1a1a", outline="")

    def _draw_level_indicator(self, width, height, level):
        """
        Rysuje wskaźnik poziomu dźwięku
        
        Args:
            width: Szerokość canvas
            height: Wysokość canvas
            level: Poziom dźwięku (0.0 - 1.0)
        """
        try:
            # Główny wskaźnik poziomu
            bar_width = int(width * 0.8)
            bar_height = 20
            bar_x = (width - bar_width) // 2
            bar_y = height // 2 - bar_height // 2
            
            # Tło wskaźnika
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                fill="#333333", outline="#666666"
            )
            
            # Wypełnienie wskaźnika
            fill_width = int(bar_width * level)
            if fill_width > 0:
                # Kolor zależny od poziomu
                if level < 0.3:
                    color = "#00ff88"
                elif level < 0.7:
                    color = "#ffff00"
                else:
                    color = "#ff4444"
                    
                self.canvas.create_rectangle(
                    bar_x, bar_y, bar_x + fill_width, bar_y + bar_height,
                    fill=color, outline=""
                )
                
        except Exception as e:
            print(f"⚠️ Błąd podczas rysowania wskaźnika: {e}")

    def _draw_waveform(self, width, height, audio_data):
        """
        Rysuje falę dźwiękową
        
        Args:
            width: Szerokość canvas
            height: Wysokość canvas
            audio_data: Lista poziomów audio
        """
        try:
            if len(audio_data) < 2:
                return
                
            # Parametry fali
            wave_height = height // 4
            wave_y = height // 2
            
            # Rysuj linię fali
            points = []
            for i, level in enumerate(audio_data):
                x = int((i / len(audio_data)) * width)
                # Dodaj animację
                wave_offset = math.sin(self.animation_frame + i * 0.2) * 5
                y = wave_y + int((level - 0.5) * wave_height) + wave_offset
                points.extend([x, y])
            
            if len(points) >= 4:  # Minimum 2 punkty (4 współrzędne)
                self.canvas.create_line(
                    points, fill=Config.WAVE_COLORS[0], width=2, smooth=True
                )
                
        except Exception as e:
            print(f"⚠️ Błąd podczas rysowania fali: {e}")

    def update_audio_level(self, audio_data: bytes):
        """
        Aktualizuje poziom audio na podstawie danych
        
        Args:
            audio_data: Surowe dane audio
        """
        try:
            # Konwertuj dane audio na poziom (0.0 - 1.0)
            if audio_data:
                # Konwertuj bytes na numpy array
                audio_array = np.frombuffer(audio_data, dtype=np.int16)
                # Oblicz RMS (Root Mean Square)
                rms = np.sqrt(np.mean(audio_array.astype(np.float32) ** 2))
                # Normalizuj do zakresu 0.0 - 1.0
                level = min(rms / 3000.0, 1.0)  # 3000 to przybliżona maksymalna wartość RMS
            else:
                level = 0.0
            
            # Aktualizuj dane w bezpieczny sposób
            with self.data_lock:
                self.audio_level = level
                self.audio_history.append(level)
                
        except Exception as e:
            print(f"⚠️ Błąd podczas aktualizacji poziomu audio: {e}")

    def hide(self):
        """Ukrywa okno (duplikat dla kompatybilności)"""
        self.command_queue.put('hide')

    def _safe_close(self):
        """Bezpieczne zamknięcie okna"""
        if self.visible:
            self.hide()