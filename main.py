#Bu kısımda Gemini'dan çok yardım aldım. Google'ı sevmem ama Gemini <3
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from PIL import Image, ImageTk
from otomasyon import otomasyonu_baslat

# Everforest tarzı
COLORS = {
    'primary': "#16291C",       
    'secondary': '#3D6B4A',      
    'background': "#F0F4F0",    
    'surface': '#E6EBE6',      
    'text_primary': '#3A3D3B',
    'text_secondary': '#6B7280', 
    'success': '#65A360',      
    'error': '#C86E5A',
    'stop': "#E6D690",          
    'error_active': '#B05C4C',   
    'border': '#A0A8A0'   
}
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)
except:
    pass
class YemekhaneGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.create_widgets()
        self.load_settings()
        self.setup_styles()
        load_dotenv()
    
    def load_settings(self):
        email = os.getenv("KTUN_EMAIL")
        password = os.getenv("KTUN_PASSWORD")
        if email: self.email_entry.insert(0, email)
        if password: self.password_entry.insert(0, password)

    def save_settings(self, email, password):
        try:
            with open(".env", "w") as f:
                f.write(f"KTUN_EMAIL={email}\n")
                f.write(f"KTUN_PASSWORD={password}\n")
        except Exception as e:
            print(f"❌ .env dosyasına yazarken hata oluştu: {e}")

    def setup_window(self): 
        self.root.title("ktunOto")
        self.root.geometry("340x780")
        self.root.configure(bg=COLORS['background'])
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.center_window()
        
    def center_window(self):
        self.root.update_idletasks()
        width, height = self.root.winfo_width(), self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Modern.TButton", font=('System', 10, 'normal'), foreground='white', background=COLORS['primary'], borderwidth=0, focuscolor='none', padding=(15, 10))
        
    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg=COLORS['background'], padx=10, pady=10)
        main_frame.pack(fill='both', expand=True)
        
        self.create_header(main_frame)
        self.create_form_fields(main_frame)
        self.create_buttons(main_frame)
        
        self.code_label = self.create_field(main_frame, "🖼️ CAPTCHA (doldurup enter'a basın)", "code")
        self.code_entry.bind("<Return>", self.save_code)

        self.image_label = tk.Label(main_frame, bg=COLORS['background'])
        self.image_label.pack(padx=10)
                
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=COLORS['background'])
        header_frame.pack(fill='x', pady=(0, 25))
        tk.Label(header_frame, text="ktunOto", font=('System', 20, 'normal'), fg=COLORS['text_primary'], bg=COLORS['background']).pack()
        tk.Label(header_frame, text="KTÜN Yemekhane Rezervasyon Otomasyonu", font=('System', 12), fg=COLORS['text_secondary'], bg=COLORS['background']).pack(pady=(3, 0))
        
    def create_form_fields(self, parent):
        form_frame = tk.Frame(parent, bg=COLORS['surface'], relief='flat', bd=0)
        form_frame.pack(fill='x', pady=(0, 15))
        inner_frame = tk.Frame(form_frame, bg=COLORS['surface'])
        inner_frame.pack(fill='both', padx=15, pady=15)
        self.create_field(inner_frame, "📧 Üniversite Num.", "email")
        self.create_field(inner_frame, "🔑 Şifre", "password", show="*")
        self.create_date_field(inner_frame)
        
    def create_field(self, parent, label_text, field_name, show=None):
        field_frame = tk.Frame(parent, bg=COLORS['surface'])
        field_frame.pack(fill='x', pady=(0, 10))
        label = tk.Label(field_frame, text=label_text, font=('System', 10, 'normal'), fg=COLORS['text_primary'], bg=COLORS['surface'], anchor='w')
        label.pack(fill='x', pady=(0, 4))
        entry = tk.Entry(field_frame, font=('System', 10), bg=COLORS['background'], fg=COLORS['text_primary'], relief='flat', bd=0, highlightthickness=2, highlightbackground=COLORS['border'], highlightcolor=COLORS['primary'], show=show)
        entry.pack(fill='x', ipady=8, ipadx=10)
        setattr(self, f"{field_name}_entry", entry)
        return label
        
    def create_date_field(self, parent):
        field_frame = tk.Frame(parent, bg=COLORS['surface'])
        field_frame.pack(fill='x', pady=(0, 10))
        tk.Label(field_frame, text="📅 Rezervasyon Tarihleri", font=('System', 10, 'normal'), fg=COLORS['text_primary'], bg=COLORS['surface'], anchor='w').pack(fill='x', pady=(0, 4))
        listbox_frame = tk.Frame(field_frame, bg=COLORS['surface'])
        listbox_frame.pack(fill='both', expand=True)
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.date_listbox = tk.Listbox(listbox_frame, selectmode='multiple', font=('System', 10), bg=COLORS['background'], fg=COLORS['text_primary'], selectbackground=COLORS['primary'], selectforeground='white', relief='flat', bd=0, height=7, yscrollcommand=scrollbar.set)
        self.date_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.date_listbox.yview)
        dates = []
        today = datetime.now()
        next_month = today.replace(day=28) + timedelta(days=4)
        last_day_of_month = (next_month - timedelta(days=next_month.day)).day
        for i in range(1, last_day_of_month - today.day + 2):
            date = today + timedelta(days=i)
            if date.month == today.month and date.weekday() < 5:
                day_name = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'][date.weekday()]
                dates.append((str(date.day), f"{date.day:02d} - {day_name} ({date.strftime('%d.%m.%Y')})"))
        for _, formatted_date in dates:
            self.date_listbox.insert(tk.END, formatted_date)
        self.date_options = dates
        
    def create_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=COLORS['background'])
        button_frame.pack(fill='x', pady=(0, 0))
        self.start_button = tk.Button(button_frame, text="🚀 Rezervasyonu Başlat", font=('System', 14, 'normal'), fg='white', bg=COLORS['primary'], activebackground=COLORS['secondary'], activeforeground='white', relief='flat', bd=0, cursor='hand2', command=self.start_automation)
        self.start_button.pack(fill='x', ipady=10, pady=(0,8))
        action_buttons_frame = tk.Frame(button_frame, bg=COLORS['background'])
        action_buttons_frame.pack(fill='x')
        self.stop_button = tk.Button(action_buttons_frame, text="⏹️ Durdur", font=('System', 10, 'normal'), fg='white', bg=COLORS['stop'], activebackground=COLORS['error_active'], activeforeground='white', relief='flat', bd=0, cursor='hand2', state='disabled', command=self.stop_automation)
        self.stop_button.pack(side=tk.LEFT, fill='x', expand=True, ipady=8, padx=(0, 4))
        self.close_button = tk.Button(action_buttons_frame, text="✖️ Kapat", font=('System', 10, 'normal'), fg='white', bg=COLORS['error_active'], activebackground=COLORS['primary'], activeforeground='white', relief='flat', bd=0, cursor='hand2', state='normal', command=self.root.quit)
        self.close_button.pack(side=tk.LEFT, fill='x', expand=True, ipady=8, padx=(4, 0))
            
    def start_automation(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        if email.endswith('@ktun.edu.tr'):
            messagebox.showerror("Hata", "Lütfen '@ktun.edu.tr' adresini silin")
            return
        self.save_settings(email, password)
        selected_indices = self.date_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Hata", "Lütfen en az bir tarih seçin!")
            return
        selected_days_list = [self.date_options[i][0] for i in selected_indices]
        self.start_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        self.stop_flag = threading.Event()
        self.automation_thread = threading.Thread(target=self.run_automation, args=(email, password, selected_days_list, self.stop_flag), daemon=True)
        self.automation_thread.start()
        self.watch_status()
    
    def save_code(self, event=None):
        code = self.code_entry.get().strip()
        if not code: return
        
        file_to_write = "sms.txt" if os.path.exists("sms_mode.flag") else "captcha.txt"
        try:
            with open(file_to_write, "w") as f:
                f.write(code)
            print(f"✅ Kod '{code}' {file_to_write} dosyasına kaydedildi.")
            self.code_entry.delete(0, tk.END)
        except Exception as e:
            print(f"❌ {file_to_write} dosyasına yazarken hata: {e}")

    def watch_status(self):
        if self.stop_flag.is_set(): return

        if os.path.exists("sms_mode.flag"):
            self.code_label.config(text="📱 SMS Kodu (doldurup enter'a basın)")
            self.image_label.config(image='', text="Lütfen telefonunuza gelen SMS kodunu girin.", font=('System', 10))
        elif os.path.exists('captcha.png'):
            try:
                image = Image.open('captcha.png')
                # Pencereye sığması için resmi yeniden boyutlandıralım.
                # Bu, arayüzün daha tutarlı görünmesini sağlar.
                max_width = 320 # Pencere genişliği (340) - yatay padding (2*10)
                aspect_ratio = image.height / image.width
                new_height = int(max_width * aspect_ratio)
                # Image.Resampling.LANCZOS daha kaliteli bir küçültme algoritmasıdır.
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo, text='')
                self.image_label.image = photo
            except Exception as e:
                if hasattr(self, 'automation_thread') and self.automation_thread.is_alive():
                    print(f"❌ CAPTCHA resmi yüklenirken hata: {e}")
        
        self.root.after(500, self.watch_status)

    def run_automation(self, email, password, date_list,stop_flag):
        try:
            otomasyonu_baslat(email, password, date_list,stop_flag)
            messagebox.showinfo("Başarılı", "Rezervasyon işlemi başarıyla tamamlandı!")
        except CredentialsError as e:
            messagebox.showerror("Kredi Kartı Hatası", str(e))
        except Exception as e:
            messagebox.showerror("Hata", f"Otomasyon sırasında beklenmedik bir hata oluştu:\n{str(e)}")
        finally:
            self.root.after(0, self.reset_ui)
            
    def stop_automation(self):
        if hasattr(self, 'stop_flag'):
            self.stop_flag.set()
        self.reset_ui()
        
    def reset_ui(self):
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled')
        self.image_label.config(image='', text='')
        self.code_label.config(text="🖼️ CAPTCHA (doldurup enter'a basın)")
        if os.path.exists("sms_mode.flag"): os.remove("sms_mode.flag")
        print("💡 Arayüz sıfırlandı. Yeni bir işlem başlatabilirsiniz.")

    def create_credentials_window(self):
        """Creates a new window for the user to enter their credit card details."""
        # setup_cc'den kaydetme fonksiyonunu import et
        from setup_cc import save_credentials

        cred_window = tk.Toplevel(self.root)
        cred_window.title("Kredi Kartı Bilgileri")
        cred_window.geometry("320x400")
        cred_window.configure(bg=COLORS['background'])
        cred_window.resizable(False, False)
        cred_window.transient(self.root) # Ana pencerenin üzerinde kalmasını sağla
        cred_window.grab_set() # Bu pencere kapanmadan ana pencereye tıklamayı engelle

        main_frame = tk.Frame(cred_window, bg=COLORS['background'], padx=15, pady=15)
        main_frame.pack(fill='both', expand=True)

        tk.Label(main_frame, text="İlk Kurulum", font=('System', 16, 'bold'), fg=COLORS['text_primary'], bg=COLORS['background']).pack(pady=(0, 5))
        tk.Label(main_frame, text="Otomasyonun ödeme yapabilmesi için\nkredi kartı bilgilerinizi girmeniz gerekiyor.\nBu bilgiler bilgisayarınızda şifrelenerek saklanır.", 
                 font=('System', 10), fg=COLORS['text_secondary'], bg=COLORS['background']).pack(pady=(0, 15))

        # --- Giriş Alanları ---
        fields = {
            "card_number": ("💳 Kart Numarası", None),
            "exp_month": ("📅 Ay (MM)", None),
            "exp_year": ("📅 Yıl (YYYY)", None),
            "cvv": ("🔒 CVV", "*")
        }
        entries = {}

        for name, (text, show) in fields.items():
            field_frame = tk.Frame(main_frame, bg=COLORS['background'])
            field_frame.pack(fill='x', pady=4)
            tk.Label(field_frame, text=text, font=('System', 10), fg=COLORS['text_primary'], bg=COLORS['background'], anchor='w').pack(fill='x')
            entry = tk.Entry(field_frame, font=('System', 10), bg=COLORS['surface'], fg=COLORS['text_primary'], relief='flat', show=show)
            entry.pack(fill='x', ipady=5)
            entries[name] = entry

        def on_save():
            card_details = {name: entry.get().strip() for name, entry in entries.items()}
            
            # Basit doğrulama
            if not all(card_details.values()):
                messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.", parent=cred_window)
                return
            
            if not card_details["card_number"].isdigit() or not (15 <= len(card_details["card_number"]) <= 16):
                messagebox.showerror("Hata", "Geçersiz Kart Numarası.", parent=cred_window)
                return

            if save_credentials(card_details):
                messagebox.showinfo("Başarılı", "Bilgileriniz başarıyla şifrelenip kaydedildi!", parent=cred_window)
                cred_window.destroy()
            else:
                messagebox.showerror("Hata", "Bilgiler kaydedilirken bir sorun oluştu.", parent=cred_window)

        # --- Butonlar ---
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(fill='x', pady=(20, 0))

        save_button = tk.Button(button_frame, text="Bilgileri Kaydet", fg='white', bg=COLORS['success'], relief='flat', command=on_save)
        save_button.pack(side='left', expand=True, ipady=8, padx=(0, 5))

        cancel_button = tk.Button(button_frame, text="Kapat", fg='white', bg=COLORS['error'], relief='flat', command=self.root.quit)
        cancel_button.pack(side='left', expand=True, ipady=8, padx=(5, 0))
        
        cred_window.wait_window() # Bu pencere kapanana kadar bekle
        
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

if __name__ == "__main__":
    app = YemekhaneGUI()
    app.run()
