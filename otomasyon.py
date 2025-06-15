#KTÜN YEMEKHANE REZERVASYON ALMA İLLETİNDEN KURTARMA SCRİPT'İ

def otomasyonu_baslat(uniemail, unisifre, alinacak_gunler_listesi,stop_flag):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service as ChromeService
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.support.ui import Select
    import time

    # tarayıcı - WebDriver'ı otomatik olarak indirir ve yönetir
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.maximize_window()
    wait = WebDriverWait(driver, 10)

    def cookie_halledici(driver):
        try:
            cookie_accept_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "btn_cookie_ok"))
            )
            cookie_accept_button.click()
            print("🍪 Cookie pop-up'ı kabul edildi.")
            time.sleep(0.14)
        except Exception:
            print("ℹ️ Cookie pop-up'ı bulunamadı veya zaten kabul edilmiş.")
            pass

    try:
        # Giriş işlemleri
        driver.get("https://yemekhane.ktun.edu.tr/User/Login")
        cookie_halledici(driver)

        wait.until(EC.presence_of_element_located((By.ID, "EPOSTA"))).send_keys(uniemail)
        driver.find_element(By.ID, "SIFRE").send_keys(unisifre)
        print("ℹ️ CAPTCHA alanını kontrol edin ve manuel olarak çözün (gerekirse). 4 saniye bekleniyor...")
        driver.find_element(By.ID, "CAPTCHA").click() 
        time.sleep(4) # Manuel CAPTCHA çözümü için bekleme süresi. Otomatik çözme sistemleri ücretli....
        driver.find_element(By.ID, "btn_Login").click()

        # yükleme beklenmesi
        time.sleep(0.3)
        wait.until(EC.visibility_of_element_located((By.LINK_TEXT, "Yemekhane Rezervasyon")))
        print("✅ Başarıyla giriş yapıldı.")

        #burada bazen hata çıkarıyor, anlayamadım.
        yemekhane_link = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Yemekhane Rezervasyon")))
        yemekhane_link.click()

        # Yemekhane ve Öğün seçimi için dropdownların yüklenmesini bekleeeee
        wait.until(EC.visibility_of_element_located((By.ID, "nYemekhane")))

        yemekhane_sec = Select(wait.until(EC.element_to_be_clickable((By.ID, "nYemekhane"))))
        yemekhane_sec.select_by_value("2") # Varsayılan değer, gerekirse değiştirin
        
        ogun_sec = Select(wait.until(EC.element_to_be_clickable((By.ID, "nOgun"))))
        ogun_sec.select_by_value("3") # Varsayılan değer, gerekirse değiştirin



        for gun_str in alinacak_gunler_listesi:
            if stop_flag.is_set():
                print("⏹️ Kullanıcı tarafından durduruldu.")
                return
            try:
                tarih_butonu_xpath = f"//*[@data-day='{gun_str}']"
                tarih_butonu = wait.until(EC.element_to_be_clickable((By.XPATH, tarih_butonu_xpath)))
                tarih_butonu.click()
                time.sleep(0.2)
                print(f"  -> {gun_str}. gün takvimden seçildi.")
            except Exception as e_date:
                print(f"  ❌ {gun_str}. gün için rezervasyon sırasında hata: {str(e_date)}")
                
        onayla_button_locator = (By.XPATH, "//button[@name='Odeme' and @value='KrediKarti' and normalize-space(text())='Onayla']")
        # "Onayla" tuşuna tekrar tekrar bastırtmadıkça olmuyor. for döngüsü ile kurtardım :>
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                onayla_button_element = wait.until(EC.element_to_be_clickable(onayla_button_locator))
                # Butonu görünür alana (merkeze) kaydır
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center'});", onayla_button_element)
                time.sleep(0.2) # Kaydırma ve olası animasyonların tamamlanması için kısa bir beklemecelerr

                onayla_button_element.click()
                print(f"'Onayla' butonuna tıklandı. Mevcut URL: {driver.current_url}")
                break # Başarılı tıklama, döngüden çık
            except Exception as e_click:
                print(f"  ⚠️ 'Onayla' butonuna tıklama denemesi {attempt + 1} başarısız: {type(e_click).__name__} - {str(e_click)}")
                if attempt == max_attempts - 1: # Son deneme ise
                    print(f"'Onayla' butonuna {max_attempts} denemeden sonra tıklanamadı.")
                    raise # Hatanın yukarıya fırlatılması
                time.sleep(1) # Tekrar denemeden önce bekle

        time.sleep(1) # Sayfanın işlenmesi için kısa bir bekleme

        print("\n🎉 Tüm belirtilen günler için rezervasyon denemeleri tamamlandı.")
    except Exception as e_main:
        print(f"💥 Ana otomasyon sürecinde (giriş vb.) bir hata oluştu: {str(e_main)}")
    finally:    
        if 'driver' in locals() and driver:
            print(f"Tarayıcı {180} saniye daha açık kalacak ve sonra kapanacak...") # 3D secure için bekleme süresi...
            time.sleep(180)
            driver.quit()
            print("Tarayıcı kapatıldı. Güle güleee")