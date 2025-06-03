import time
import threading
import mouse # Untuk kontrol mouse
import keyboard # Untuk kontrol keyboard

# Variabel global untuk mengontrol status klik
clicking = False
stop_event = threading.Event()
click_thread = None

def perform_click():
    """Melakukan satu kali klik mouse kiri pada posisi kursor saat ini."""
    mouse.click('left')

def auto_clicker(delay_ms, num_clicks_str):
    """Fungsi utama untuk melakukan klik otomatis."""
    global clicking
    clicking = True
    print(f"Memulai klik otomatis dengan jeda {delay_ms} ms.")

    if num_clicks_str.lower() == 'inf':
        num_clicks = float('inf')
        print("Klik akan berjalan tanpa batas hingga dihentikan (Tekan 's' lagi).")
    else:
        try:
            num_clicks = int(num_clicks_str)
            if num_clicks <= 0:
                print("Jumlah klik harus lebih dari 0.")
                clicking = False
                return
            print(f"Akan melakukan {num_clicks} klik.")
        except ValueError:
            print("Jumlah klik tidak valid. Masukkan angka atau 'inf'.")
            clicking = False
            return

    clicks_done = 0
    while clicking and clicks_done < num_clicks:
        if stop_event.is_set():
            break
        perform_click()
        clicks_done += 1
        if clicks_done < num_clicks: # Hanya tidur jika masih ada klik selanjutnya
            time.sleep(delay_ms / 1000.0) # Konversi milidetik ke detik
        if clicks_done % 10 == 0 and num_clicks == float('inf'):
             print(f"{clicks_done} klik telah dilakukan...")


    if not stop_event.is_set(): # Hanya cetak jika tidak dihentikan secara paksa
        print("Klik otomatis selesai.")
    clicking = False
    stop_event.clear()

def toggle_clicking():
    """Memulai atau menghentikan proses klik otomatis."""
    global clicking, click_thread, stop_event

    if clicking:
        print("Menghentikan klik otomatis...")
        stop_event.set()
        if click_thread and click_thread.is_alive():
            click_thread.join()
        clicking = False
        print("Klik otomatis dihentikan.")
    else:
        if click_thread and click_thread.is_alive():
            print("Proses klik sebelumnya masih menyelesaikan, harap tunggu.")
            return

        try:
            delay_input = input("Masukkan jeda antar klik (dalam milidetik): ")
            delay_ms = int(delay_input)
            if delay_ms <= 0:
                print("Jeda harus lebih dari 0 milidetik.")
                return

            num_clicks_input = input("Masukkan jumlah klik (angka, atau 'inf' untuk tak terbatas): ")

            stop_event.clear()
            click_thread = threading.Thread(target=auto_clicker, args=(delay_ms, num_clicks_input))
            click_thread.start()

        except ValueError:
            print("Input jeda tidak valid. Harap masukkan angka.")
        except Exception as e:
            print(f"Terjadi kesalahan: {e}")

def main():
    """Fungsi utama untuk menjalankan program."""
    print("--- Auto Clicker Sederhana (Alternatif) ---")
    print("Tekan 's' untuk memulai/menghentikan klik otomatis.")
    print("Tekan 'q' untuk keluar dari program.")
    print("-------------------------------------------")
    print("PENTING: Pastikan kursor mouse berada pada posisi yang diinginkan sebelum menekan 's'.")
    print("CATATAN: Program ini mungkin memerlukan hak akses administrator (root) untuk fungsi keyboard.")

    # Menambahkan hotkey
    # `suppress=True` mencegah event tombol 's' diketik di aplikasi lain saat program berjalan
    # Namun, ini bisa mengganggu jika pengguna benar-benar ingin mengetik 's'
    # Jadi, kita bisa menghapusnya atau menggantinya dengan `keyboard.on_press_key("s", lambda _: toggle_clicking())`
    # yang memungkinkan event terus berlanjut. Untuk kasus ini, tidak men-suppress mungkin lebih baik.

    keyboard.add_hotkey('s', toggle_clicking)
    keyboard.add_hotkey('S', toggle_clicking) # Untuk Shift + s

    print("Listener keyboard aktif. Tekan 's' atau 'q'.")

    # Menjaga program tetap berjalan hingga 'q' ditekan
    # `keyboard.wait('q')` akan memblokir hingga 'q' ditekan
    # dan kemudian menghentikan semua hotkey yang terdaftar.
    try:
        keyboard.wait('q', suppress=True) # Menunggu tombol 'q' untuk keluar
        print("\nTombol 'q' ditekan. Keluar dari program...")
    except Exception as e:
        print(f"Error saat menunggu tombol keluar: {e}")
    finally:
        global clicking, stop_event, click_thread
        if clicking: # Jika sedang mengklik saat 'q' ditekan
            stop_event.set()
            if click_thread and click_thread.is_alive():
                click_thread.join()
        keyboard.remove_all_hotkeys() # Membersihkan semua hotkey


if __name__ == "__main__":
    main()