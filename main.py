   #Bu kısımda Gemini'dan çok yardım aldım. google'dan nefret ederim ama Allah razı olsun
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Everforest tarzı
# Kendi tarzını oluşturmak istersen uyg'un ss'ini al ve sırayla renkleri değiştirmen yeterli. 
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

        if email:
            self.email_entry.insert(0, email)
        if password:
            self.password_entry.insert(0, password)

    def save_settings(self, email, password):
        try:
            with open(".env", "w") as f:
                f.write(f"KTUN_EMAIL={email}\n")
                f.write(f"KTUN_PASSWORD={password}\n")
            print("✅ Bilgiler .env dosyasına kaydedildi.")
        except Exception as e:
            print(f"❌ .env dosyasına yazarken hata oluştu: {e}")

    def setup_window(self): 
        self.root.title("ktunOto")
        self.root.geometry("340x550")
        self.root.configure(bg=COLORS['background'])
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.center_window()
        
    def center_window(self): #Uygulama ekranın ortasında yüklensin diye
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_styles(self):
        style = ttk.Style()
    
        style.configure(
            "Modern.TButton",
            font=('System', 10, 'normal'),
            foreground='white',
            background=COLORS['primary'],
            borderwidth=0,
            focuscolor='none',
            padding=(15, 10)
        )
        
        style.configure(
            "Modern.TCombobox",
            font=('System', 10),
            borderwidth=2,
            relief='solid',
            bordercolor=COLORS['border'],
            padding=(10, 8),
            fieldbackground=COLORS['background'],
            foreground=COLORS['text_primary']
        )
        style.map(
            "Modern.TCombobox",
            bordercolor=[
                ('readonly', COLORS['border']),
                ('focus', COLORS['primary']),
                ('hover', COLORS['secondary'])
            ],
            fieldbackground=[('readonly', COLORS['background'])],
            selectbackground=[('readonly', COLORS['background'])], # Entry kısmının arka planı
            selectforeground=[('readonly', COLORS['text_primary'])]  # Entry kısmının metin rengi
        )
        # Combobox açılır liste stil ayarları
        self.root.option_add('*TCombobox*Listbox.font', ('System', 10)) # Bu satırlar artık Listbox için geçerli değil ama bırakılabilir veya kaldırılabilir.
        self.root.option_add('*TCombobox*Listbox.background', COLORS['surface']) # Listbox için ayrıca stil gerekebilir.
        self.root.option_add('*TCombobox*Listbox.foreground', COLORS['text_primary']) # Listbox için ayrıca stil gerekebilir.
        self.root.option_add('*TCombobox*Listbox.selectBackground', COLORS['primary']) # Listbox için ayrıca stil gerekebilir.
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white') # Listbox için ayrıca stil gerekebilir.
        self.root.option_add('*TCombobox*Listbox.relief', 'flat')
        self.root.option_add('*TCombobox*Listbox.bd', 0)
        self.root.option_add('*TCombobox*Listbox.highlightthickness', 0)
        
    def create_widgets(self):
        # Ana container
        main_frame = tk.Frame(self.root, bg=COLORS['background'], padx=10, pady=10) # Padding azaltıldı
        main_frame.pack(fill='both', expand=True)
        
        # Header
        self.create_header(main_frame)
        
        # Form alanları
        self.create_form_fields(main_frame)
        
        # Butonlar
        self.create_buttons(main_frame)
                
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=COLORS['background'])
        header_frame.pack(fill='x', pady=(0, 15)) # Padding azaltıldı
        
        # Ana başlık
        title_label = tk.Label(
            header_frame,
            text="ktunOto",
            font=('System', 20, 'normal'),
            fg=COLORS['text_primary'],
            bg=COLORS['background']
        )
        title_label.pack()
        
        # Alt başlık
        subtitle_label = tk.Label(
            header_frame,
            text="KTÜN Yemekhane Rezervasyon Otomasyonu",
            font=('System', 12),
            fg=COLORS['text_secondary'],
            bg=COLORS['background']
        )
        subtitle_label.pack(pady=(3, 0)) # Padding azaltıldı
        
    def create_form_fields(self, parent):
        # Form container
        form_frame = tk.Frame(parent, bg=COLORS['surface'], relief='flat', bd=0)
        form_frame.pack(fill='x', pady=(0, 15)) # Padding azaltıldı
        
        # Padding için iç frame
        inner_frame = tk.Frame(form_frame, bg=COLORS['surface'])
        inner_frame.pack(fill='both', padx=15, pady=15) # Padding azaltıldı
        
        # Email field
        self.create_field(inner_frame, "📧 Üniversite Num.", "email")
        
        # Password field
        self.create_field(inner_frame, "🔑 Şifre", "password", show="*")
        
        # Tarih field
        self.create_date_field(inner_frame)
        
    def create_field(self, parent, label_text, field_name, show=None):
        field_frame = tk.Frame(parent, bg=COLORS['surface'])
        field_frame.pack(fill='x', pady=(0, 10)) # Padding azaltıldı
        
        # Label
        label = tk.Label(
            field_frame,
            text=label_text,
            font=('System', 10, 'normal'),
            fg=COLORS['text_primary'],
            bg=COLORS['surface'],
            anchor='w'
 )

        label.pack(fill='x', pady=(0, 4)) # Padding azaltıldı

        # Entry
        entry = tk.Entry(
            field_frame,
            font=('System', 10),
            bg=COLORS['background'], # Arka plan rengi temaya uyarlandı
            fg=COLORS['text_primary'],
            relief='flat',          # Kenarlık stili flat yapıldı
            bd=0,                   # relief='flat' için bd=0
            highlightthickness=2,   # Odak/kenarlık için
            highlightbackground=COLORS['border'], # Odaklanılmamış kenarlık rengi
            highlightcolor=COLORS['primary'],     # Odaklanılmış kenarlık rengi
            show=show
        )
        entry.pack(fill='x', ipady=8, ipadx=10) # İç padding azaltıldı
        
        setattr(self, f"{field_name}_entry", entry)
        
    def create_date_field(self, parent):
        # Tarih seçimi için frame
        field_frame = tk.Frame(parent, bg=COLORS['surface'])
        field_frame.pack(fill='x', pady=(0, 10)) # Padding azaltıldı
        
        # Label
        label = tk.Label(
            field_frame,
            text="📅 Rezervasyon Tarihleri",
            font=('System', 10, 'normal'),
            fg=COLORS['text_primary'],
            bg=COLORS['surface'],
            anchor='w'
        )
        label.pack(fill='x', pady=(0, 4)) # Padding azaltıldı
        
        # Tarih seçimi için Listbox
        # Scrollbar ekleyelim
        listbox_frame = tk.Frame(field_frame, bg=COLORS['surface'])
        listbox_frame.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.date_listbox = tk.Listbox(
            listbox_frame,
            selectmode='multiple', # Tıklayarak tek tek seç/kaldır
            font=('System', 10),
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            selectbackground=COLORS['primary'],
            selectforeground='white',
            relief='flat',
            bd=0,
            height=7, # Gösterilecek satır sayısı
            yscrollcommand=scrollbar.set # Scrollbar'ı Listbox'a bağla
        )
        self.date_listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=self.date_listbox.yview) # Listbox'ı Scrollbar'a bağla

        # Tarih seçeneklerini doldur
        dates = []
        today = datetime.now()
        current_day = today.day
        current_month = today.month
        current_year = today.year

        # Ayın son gününü bul
        next_month = today.replace(day=28) + timedelta(days=4)  # Bir sonraki ayın başına gitmek için güvenli bir yol
        last_day_of_month = (next_month - timedelta(days=next_month.day)).day

        for i in range(1, last_day_of_month - current_day + 2): # Yarından ay sonuna kadar (+1 gün yarın için, +1 gün range sonu için)
            date = today + timedelta(days=i)
            # Sadece mevcut ayın günlerini ve hafta içini al
            if date.month == current_month and date.weekday() < 5: # Pazartesi (0) - Cuma (4)
            # Hafta sonu (Cumartesi: 5, Pazar: 6) günlerini atla
                day_name = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma'][date.weekday()]
                formatted_date = f"{date.day:02d} - {day_name} ({date.strftime('%d.%m.%Y')})"
                dates.append((str(date.day), formatted_date))

        # Listbox'a tarihleri ekle
        for _, formatted_date in dates:
            self.date_listbox.insert(tk.END, formatted_date)
        
        # İlk tarihin otomatik seçilmesini engellemek için aşağıdaki satırlar yorumlandı
        # if self.date_listbox.size() > 0:
        #     self.date_listbox.selection_set(0)
            
        self.date_options = dates
        
    def create_buttons(self, parent):
        button_frame = tk.Frame(parent, bg=COLORS['background'])
        button_frame.pack(fill='x', pady=(0, 0)) # Üst padding kaldırıldı
        
        # Rezervasyon başlat butonu
        self.start_button = tk.Button(
            button_frame,
            text="🚀 Rezervasyonu Başlat",
            font=('System', 14, 'normal'),
            fg='white',
            bg=COLORS['primary'],
            activebackground=COLORS['secondary'],
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            command=self.start_automation
        )
        self.start_button.pack(fill='x', ipady=10, pady=(0,8)) # Alt boşluk eklendi
        
        # Hover efektleri
        self.start_button.bind('<Enter>', lambda e: self.on_button_hover(e, True))
        self.start_button.bind('<Leave>', lambda e: self.on_button_hover(e, False))
        
        # Aksiyon butonları için frame (Durdur ve Kapat)
        action_buttons_frame = tk.Frame(button_frame, bg=COLORS['background'])
        action_buttons_frame.pack(fill='x')

        # Durdur butonu (Artık sadece durdurma işlevi görecek)
        self.stop_button = tk.Button(
            action_buttons_frame,
            text="⏹️ Durdur", # Metin her zaman "Durdur"
            font=('System', 10, 'normal'), # Font boyutu küçültüldü
            fg='white',
            bg=COLORS['stop'], # Hata rengi kullanılıyor
            activebackground=COLORS['error_active'], # Hata renginin aktif tonu
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            state='disabled', # Başlangıçta devre dışı
            command=self.stop_automation
        )
        self.stop_button.pack(side=tk.LEFT, fill='x', expand=True, ipady=8, padx=(0, 4)) # Sol tarafa, boşluklu

        # Kapat butonu
        self.close_button = tk.Button(
            action_buttons_frame,
            text="✖️ Kapat",
            font=('System', 10, 'normal'),
            fg='white',
            bg=COLORS['error_active'], # Farklı bir renk (örneğin ikincil tema rengi)
            activebackground=COLORS['primary'], # Aktif durum için farklı renk
            activeforeground='white',
            relief='flat',
            bd=0,
            cursor='hand2',
            state='normal', # Her zaman aktif
            command=self.root.quit # Uygulamayı kapatır
        )
        self.close_button.pack(side=tk.LEFT, fill='x', expand=True, ipady=8, padx=(4, 0)) # Sağ tarafa, boşluklu
         
    def on_button_hover(self, event, hovered):
        if hovered:
            event.widget.configure(bg=COLORS['secondary'])
        else:
            event.widget.configure(bg=COLORS['primary'])
            
    def start_automation(self):
        # Form validasyonu
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not email or not password:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun!")
            return
            
        if email.endswith('@ktun.edu.tr'):
            messagebox.showerror("Hata", "Lütfen '@ktun.edu.tr' adresini silin")
            return
        
        # Başarılı giriş denemesi öncesi e-postayı kaydet
        self.save_settings(email, password) # Şifre de gönderiliyor
            
        # Seçilen tarihleri al
        selected_indices = self.date_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Hata", "Lütfen en az bir tarih seçin!")
            return
            
        # Seçilen indekslere karşılık gelen gün numaralarını al
        selected_days_list = [self.date_options[i][0] for i in selected_indices]
        print(f"Seçilen günler: {selected_days_list}") # Debug amaçlı
        
        # UI durumunu güncelle
        self.start_button.configure(state='disabled') # Butonu devre dışı bırak
        self.stop_button.configure(state='normal') # Durdur butonunu aktif et (metin zaten "⏹️ Durdur")
        # self.close_button.configure(state='disabled') # İsteğe bağlı: Otomasyon sırasında kapatma butonunu devre dışı bırakabilirsiniz
        # self.progress.start(10) # self.progress is not initialized. Create it in create_widgets if needed.
        print("🔄 Otomasyon başlatılıyor...") # Placeholder for status update
        
        # Otomasyonu thread'de çalıştır
        self.stop_flag = threading.Event()
        self.automation_thread = threading.Thread(
            target=self.run_automation,
            args=(email, password, selected_days_list,self.stop_flag), # Liste olarak gönder
            daemon=True
        )
        self.automation_thread.start()  
    
    def run_automation(self, email, password, date_list,stop_flag): # Parametre adını listeye göre güncelle
        try:
            # Otomasyon fonksiyonunu import et ve çalıştır
            from otomasyon import otomasyonu_baslat
            
            print("🌐 Web sitesine bağlanılıyor...") # Placeholder for status update
            otomasyonu_baslat(email, password, date_list,stop_flag)
            
            print("✅ Rezervasyon tamamlandı!") # Placeholder for status update
            messagebox.showinfo("Başarılı", "Rezervasyon işlemi tamamlandı!")
            
        except Exception as e:
            print(f"❌ Hata: {str(e)}") # Placeholder for status update
            messagebox.showerror("Hata", f"Otomasyon sırasında hata oluştu:\n{str(e)}")
            
        finally:
            self.root.after(0, self.reset_ui)
            
    def stop_automation(self):
        # Otomasyon thread'inin çalışıp çalışmadığını kontrol et
        if hasattr(self, 'stop_flag'):
            self.stop_flag.set() 
            print("Kullanıcı otomasyonu durdurma isteğinde bulundu. UI sıfırlanıyor.")
        self.reset_ui() # UI'ı sıfırla (Durdur butonunu devre dışı bırakacak)
        
    def reset_ui(self):
        self.start_button.configure(state='normal')
        self.stop_button.configure(state='disabled') # Durdur butonunu devre dışı bırak (metin "⏹️ Durdur" kalır)
        # self.progress.stop() # self.progress is not initialized. Create it in create_widgets if needed.
        print("💡 Bilgilerinizi girin ve rezervasyonu başlatın") # Placeholder for status update
        
    def run(self):
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.root.quit()

if __name__ == "__main__":
    app = YemekhaneGUI()
    app.run()
    #bu kadardı :)