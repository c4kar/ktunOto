#KTÜN YEMEKHANE REZERVASYON ALMA İLLETİNDEN KURTARMA SCRİPTİ
import os
from cryptography.fernet import Fernet

class CredentialsError(Exception):
    """Custom exception for errors related to credential loading."""
    pass

def decrypt_credentials():
    """
    Loads the encryption key and decrypts the credit card data.
    Returns a dictionary with the credit card details.
    Raises CredentialsError if files are not found or corrupt.
    """
    try:
        key = open("secret.key", "rb").read()
        encrypted_data = open("cc.dat", "rb").read()
        
        f = Fernet(key)
        decrypted_data = f.decrypt(encrypted_data).decode()
        
        parts = decrypted_data.split('|')
        if len(parts) != 5:
            raise CredentialsError("Şifrelenmiş veri dosyası bozuk veya geçersiz.")
            
        return {
            'card_number': parts[0],
            'card_holder': parts[1],
            'exp_month': parts[2],
            'exp_year': parts[3],
            'cvv': parts[4]
        }
    except FileNotFoundError:
        raise CredentialsError("Kredi kartı bilgileri (cc.dat) veya anahtar (secret.key) bulunamadı.\nLütfen önce 'setup_cc.py' betiğini çalıştırın.")
    except Exception as e:
        raise CredentialsError(f"Kredi kartı bilgileri okunurken bir hata oluştu: {e}")

def otomasyonu_baslat(uniemail, unisifre, alinacak_gunler_listesi,stop_flag):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import Select
    from selenium.webdriver.chrome.options import Options
    import time

    cc_info = decrypt_credentials()
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    wait = WebDriverWait(driver, 20)

    if os.path.exists("sms_mode.flag"): os.remove("sms_mode.flag")
    if os.path.exists("sms.txt"): os.remove("sms.txt")

    def cookie_halledici(driver):
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "btn_cookie_ok"))).click()
            print("🍪 Cookie pop-up'ı kabul edildi.")
        except Exception:
            print("ℹ️ Cookie pop-up'ı bulunamadı veya zaten kabul edilmiş.")
    
    try:
        driver.get("https://yemekhane.ktun.edu.tr/User/Login")
        cookie_halledici(driver)

        wait.until(EC.presence_of_element_located((By.ID, "EPOSTA"))).send_keys(uniemail)
        driver.find_element(By.ID, "SIFRE").send_keys(unisifre)
        
        captcha_image = wait.until(EC.presence_of_element_located((By.ID, "img_captcha")))
        captcha_image.screenshot('captcha.png')
        print("🖼️ CAPTCHA resmi indirildi: captcha.png")

        if os.path.exists("captcha.txt"): os.remove("captcha.txt")

        captcha_code = None
        timeout = 60
        start_time = time.time()
        while time.time() - start_time < timeout:
            if stop_flag.is_set(): return
            if os.path.exists("captcha.txt"):
                with open("captcha.txt", "r") as f: captcha_code = f.read().strip()
                if len(captcha_code) == 4:
                    os.remove("captcha.txt")
                    print(f"CAPTCHA '{captcha_code}' alındı.")
                    break
                else:
                    captcha_code = None 
            time.sleep(0.5)

        if not captcha_code:
            raise Exception("4 haneli CAPTCHA girişi zaman aşımına uğradı veya alınamadı.")

        driver.find_element(By.ID, "CAPTCHA").send_keys(captcha_code)
        driver.find_element(By.ID, "btn_Login").click()

        print("✅ Başarıyla giriş yapıldı.")

        # "Yemekhane Rezervasyon" linkine tıkla (CSS Selector ile daha sağlam)
        rezervasyon_link_selector = "a[href='/Yemek/Rezervasyon']"
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, rezervasyon_link_selector))).click()

        # Yemekhane ve Öğün seçimi
        wait.until(EC.visibility_of_element_located((By.ID, "nYemekhane")))
        Select(wait.until(EC.element_to_be_clickable((By.ID, "nYemekhane")))).select_by_value("2")
        Select(wait.until(EC.element_to_be_clickable((By.ID, "nOgun")))).select_by_value("3")

        for gun_str in alinacak_gunler_listesi:
            if stop_flag.is_set(): return
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[@data-day='{gun_str}']"))).click()
                print(f"  -> {gun_str}. gün takvimden seçildi.")
            except Exception as e_date:
                print(f"  ❌ {gun_str}. gün için rezervasyon sırasında hata: {str(e_date)}")
                
        # "Onayla" butonuna tıkla (JavaScript click ile daha sağlam)
        onayla_button_css = ".form-group > .button_utarit_yellow"
        try:
            onayla_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, onayla_button_css)))
            driver.execute_script("arguments[0].scrollIntoView(true);", onayla_button)
            time.sleep(0.5) # Scroll sonrası sayfanın oturması için kısa bekleme 
            driver.execute_script("arguments[0].click();", onayla_button)
            print("'Onayla' butonuna tıklandı. Ödeme sayfasına yönlendiriliyor...")
        except Exception as e:
            print(f"💥 'Onayla' butonuna tıklanırken bir hata oluştu: {e}")
            print("Sayfa yapısı değişmiş olabilir. Lütfen butonu manuel olarak kontrol edin.")
            raise # Hatanın yukarıya fırlatılması
        
        # --- KREDİ KARTI & 3D SECURE --- #
        try:
            print("💳 Ödeme formuna geçiliyor...")
            
            # 1. iFrame'e geçiş yap (Ödeme formları genellikle bir iFrame içindedir)
            # Not: iFrame'in ID'si, ismi veya indeksi farklı olabilir. Genellikle tek iframe olur.
            try:
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
                print("🖼️ Ödeme formu iFrame'ine geçiş yapıldı.")
            except Exception as e_iframe:
                print(f"⚠️ iFrame bulunamadı veya geçiş yapılamadı: {e_iframe}")
                print("    Formun bir iFrame içinde olmadığı varsayılarak devam ediliyor.")

            # 2. Formu doldur
            print(" Kredi kartı bilgileri dolduruluyor...")
            card_number_field = wait.until(EC.presence_of_element_located((By.ID, 'pan')))
            card_number_field.send_keys(cc_info['card_number'])
            print("  -> Kart numarası girildi.")
            
            Select(driver.find_element(By.ID, 'selectMonth')).select_by_value(cc_info['exp_month'])
            print("  -> Ay seçildi.")

            Select(driver.find_element(By.ID, 'selectYear')).select_by_value(cc_info['exp_year'])
            print("  -> Yıl seçildi.")

            driver.find_element(By.ID, 'cv2').send_keys(cc_info['cvv'])
            print("  -> CVV girildi.")
            
            # 3. Ödeme butonuna tıkla
            driver.find_element(By.ID, 'btnSbmt').click()
            print("✅ Ödeme bilgileri gönderildi. 3D Secure onayı bekleniyor...")

            # 4. Ana sayfaya geri dön (3D Secure sayfası genellikle ana sayfadadır)
            driver.switch_to.default_content()
            print("🖼️ Ana sayfaya geri dönüldü.")

            # --- 3D SECURE (SMS KODU) --- #
            with open("sms_mode.flag", "w") as f: f.write('1')
            
            sms_code = None
            timeout = 180
            start_time = time.time()
            print("📱 Telefona gelen SMS kodunun girilmesi bekleniyor...")
            while time.time() - start_time < timeout:
                if stop_flag.is_set(): return
                if os.path.exists("sms.txt"):
                    with open("sms.txt", "r") as f: sms_code = f.read().strip()
                    if sms_code:
                        os.remove("sms.txt")    
                        print(f"SMS kodu '{sms_code}' alındı.")
                        break
                time.sleep(0.5)

            if not sms_code:
                raise Exception("SMS kodu girişi zaman aşımına uğradı veya alınamadı.")

            # 3D Secure formu da bir iFrame içinde olabilir, bu bankaya bağlıdır.
            # Gerekirse burada tekrar bir iFrame'e geçiş yapılmalıdır.
            print("🖼️ 3D Secure iFrame'i aranıyor...")
            try:
                # Bankadan bankaya iFrame değişebilir, genel bir arama yapılıyor.
                # Genellikle 3D Secure formu yeni bir iFrame'de olur.
                wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
                print("  -> 3D Secure iFrame'ine geçiş yapıldı.")
            except Exception as e_iframe_3d:
                print(f"⚠️ 3D Secure iFrame'i bulunamadı: {e_iframe_3d}")
                print("    Sayfanın ana içeriğinde devam ediliyor, bu hataya neden olabilir.")

            # SMS kodunu girmek için alanı bul ve doldur. Yaygın ID'ler deneniyor.
            otp_input_field = None
            possible_otp_ids = ['otpCode', 'code', 'smsCode', 'authCode']
            for an_id in possible_otp_ids:
                try:
                    otp_input_field = wait.until(EC.presence_of_element_located((By.ID, an_id)))
                    print(f"  -> SMS giriş alanı bulundu (ID: {an_id}).")
                    break 
                except:
                    print(f"  -> SMS giriş alanı ID '{an_id}' ile bulunamadı.")
            
            if not otp_input_field:
                raise Exception("SMS kodu giriş alanı web sayfasında bulunamadı. ID'ler değişmiş olabilir.")
                
            otp_input_field.send_keys(sms_code)

            # Onay butonuna tıkla. Yaygın ID/metinler deneniyor.
            commit_button = None
            possible_buttons = [
                (By.ID, 'btn-commit'),
                (By.ID, 'submit'),
                (By.XPATH, "//button[contains(text(), 'Onayla')]"),
                (By.XPATH, "//button[contains(text(), 'Submit')]"),
                (By.XPATH, "//button[contains(text(), 'Gönder')]")
            ]
            for by, val in possible_buttons:
                try:
                    commit_button = wait.until(EC.element_to_be_clickable((by, val)))
                    print(f"  -> Onay butonu bulundu ({by}: {val}).")
                    break
                except:
                    print(f"  -> Onay butonu bulunamadı ({by}: {val}).")

            if not commit_button:
                raise Exception("SMS onay butonu web sayfasında bulunamadı. Buton metni/ID'si değişmiş olabilir.")

            commit_button.click()
            print("✅ SMS kodu gönderildi. Ödeme tamamlanıyor...")
            
            # Ana içeriğe geri dön
            driver.switch_to.default_content()
            time.sleep(5) # Sayfanın işlenmesi için bekle
            print("🎉 Rezervasyon ve ödeme işlemi başarıyla tamamlandı!")

        except Exception as e_payment:
            print(f"💥 Ödeme/3D Secure formunu doldururken bir hata oluştu: {str(e_payment)}")
            print("Lütfen tarayıcı penceresini kontrol edin.")
            print("Hatanın nedeni büyük ihtimalle ödeme sayfasındaki element ID'lerinin (pan, selectMonth, cv2, btnSbmt, otpCode, vb.) veya iFrame yapısının yanlış olmasıdır.")
            # Hata durumunda ana sayfaya dönmeyi dene ki tarayıcı kontrol edilebilsin
            try:
                driver.switch_to.default_content()
            except: pass
            raise e_payment

    except Exception as e_main:
        print(f"💥 Ana otomasyon sürecinde bir hata oluştu: {str(e_main)}")
        raise e_main

    finally:    
        if 'driver' in locals() and driver:
            print(f"Tarayıcı {15} saniye içinde kapanacak...")
            time.sleep(15)
            driver.quit()
            print("Tarayıcı kapatıldı. Güle güleee")
        # Temizlik
        if os.path.exists('captcha.png'): os.remove('captcha.png')
        if os.path.exists('captcha.txt'): os.remove('captcha.txt')
        if os.path.exists('sms_mode.flag'): os.remove('sms_mode.flag')
        if os.path.exists('sms.txt'): os.remove('sms.txt')
    