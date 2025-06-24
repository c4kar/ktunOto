<p align="center">
<img width="75%" src="https://github.com/c4kar/ktunOto/blob/main/logo.png?raw=true" title="ktunOto logo" />
</p>

<p align="center">
🤖<i> KTÜN Rezervasyon alma illetinden kurtulma programı </i>👾
</p>


## ⚡ Hızlı Tanıtım
**ktunOto**, *KTÜN Yemekhane Rezervasyon Sistemi* üzerinden çok daha hızlı öğün rezerve etmenizi sağlayan, python-selenium ile oluşturulmuş bir öğrenci programıdır. Bilgilerinizi hatırlamayan, tarayıcalarda düzgün çalışmayan, okulumuza yakışmayan [sitemizi](https://yemekhane.ktun.edu.tr/User/Login) kullanmaktan sıkılanlar için üretilmiştir.

<p align="center">
<img width="50%" src="https://github.com/c4kar/ktunOto/blob/main/g%C3%B6rsel/ui.png?raw="true" title="ui"/>
</p>

## 🛠️ Proje Açıklaması

**ktunOto**, KTÜNYS'yi otomatikleştiren bir **masaüstü** uygulamadır. Arayüz üzerinden üniversite numarası, şifre ve istenilen tarihleri seçtikten sonra program Selenium ile web sitesine girer, *CAPTCHA* dışındaki adımları otomatik tamamlar ve sizi ödeme ekranına getirir.

## 📋 Gerekenler

- python 
	+ selenium
	+ webdriver-manager
	+ python-dotenv



## 💻 Nasıl Kullanbilirim?

1. **installer.py ile doğrudan kurabilirsin (Tavsiye edilir)**:  

   ```bash
   curl -sL https://github.com/c4kar/ktunOto/blob/main/installer.py | python
2. **.zip şeklinde indirip main.py dosyasını çalıştırabilirsin**
	1. zip'ten çıkarttıktan sonra **cmd** ile klasöre gelip aşağıdaki kod satırını yazmanız yeterli.	
		```bash
  	 	pip install -r requirements.txt
		```
	2. main.py dosyasını çalıştır.

## ⚠️ Notlar
Programı ilk defa çalıştırdığınızda tarayıcı sürücüsünü indirdiğinden dolayı yavaş açılabilir. Sadece ilk çalıştırma için geçerlidir.
