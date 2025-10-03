"""
Główny plik uruchamiający aplikację Voice Notes
"""
import tkinter as tk
import sys
from voice_notes_app import VoiceNotesApp


def main():
    """Funkcja główna aplikacji"""
    # Główny root Tk musi być utworzony w głównym wątku
    root = tk.Tk()
    
    # Ukryj główne okno (używamy tylko Toplevel do nagrywania)
    try:
        root.withdraw()
    except Exception:
        pass

    app = None
    try:
        # Utwórz i uruchom aplikację
        app = VoiceNotesApp(root)
        
        if app.run():
            # Pętla główna Tkinter (blokuje do zamknięcia)
            root.mainloop()
        else:
            print("❌ Nie udało się uruchomić aplikacji")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n👋 Przerwano przez użytkownika...")
        
    except Exception as e:
        print(f"❌ Błąd krytyczny: {e}")
        input("Naciśnij Enter aby zakończyć...")
        
    finally:
        # Zamknij aplikację i zwolnij zasoby
        if app:
            app.shutdown()


if __name__ == "__main__":
    main()