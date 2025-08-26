from cryptography.fernet import Fernet
import os
import datetime

KEY_FILE = "secret.key"
DATA_FILE = "cc.dat"

def generate_key():
    """
    Generates a new encryption key and saves it to a file.
    If a key file already exists, it does nothing.
    """
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)
        print(f"✨ Yeni bir şifreleme anahtarı oluşturuldu ve '{KEY_FILE}' dosyasına kaydedildi.")
        print("⚠️ BU ANAHTAR DOSYASINI GÜVENDE TUTUN VE KESİNLİKLE PAYLAŞMAYIN!")
    else:
        print(f"ℹ️ '{KEY_FILE}' zaten mevcut. Yeni anahtar oluşturulmadı.")

def load_key():
    """Loads the encryption key from the key file."""
    return open(KEY_FILE, "rb").read()

def save_credentials(card_details: dict):
    """
    Encrypts the given card details and saves them to the data file.
    Also generates a key if it doesn't exist.
    
    Args:
        card_details (dict): A dictionary containing 'card_number',
                             'exp_month', 'exp_year', and 'cvv'.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        generate_key()
        key = load_key()
        f = Fernet(key)

        # Verileri birleştirme
        credentials_str = (
            f"{card_details['card_number']}|"
            f"{card_details['exp_month']}|"
            f"{card_details['exp_year']}|"
            f"{card_details['cvv']}"
        )
        
        encrypted_credentials = f.encrypt(credentials_str.encode())

        with open(DATA_FILE, "wb") as data_file:
            data_file.write(encrypted_credentials)
            
        print(f"\n✅ Kredi kartı bilgileriniz şifrelendi ve '{DATA_FILE}' dosyasına başarıyla kaydedildi.")
        return True
    except Exception as e:
        print(f"\n❌ Bilgiler kaydedilirken bir hata oluştu: {e}")
        return False

def get_credentials_from_user():
    """
    Prompts the user for credit card details via command line and validates them.
    """
    print("\n--- Kredi Kartı Bilgilerinizi Girin ---")
    print("Bu bilgiler şifrelenerek yerel olarak saklanacaktır.")
    
    while True:
        card_number = input("💳 Kart Numarası (16 hane, boşluksuz): ").strip()
        if card_number.isdigit() and 15 <= len(card_number) <= 16:
            break
        else:
            print("❌ Geçersiz kart numarası. Lütfen 15-16 haneli ve sadece rakamlardan oluşan bir numara girin.")

    while True:
        exp_month = input("📅 Son Kullanma Ay (MM, örn: 01, 09): ").strip()
        if exp_month.isdigit() and 1 <= int(exp_month) <= 12 and len(exp_month) == 2:
            break
        else:
            print("❌ Geçersiz ay. Lütfen 1-12 arasında 2 haneli bir sayı girin (örn: 05).")

    while True:
        exp_year = input("📅 Son Kullanma Yıl (YYYY, örn: 2025, 2028): ").strip()
        if exp_year.isdigit() and len(exp_year) == 4:
            try:
                full_year = int(exp_year)
                # Ayın son gününü bularak geçerli bir son kullanma tarihi oluştur
                # Örn: 02/2025 -> 2025-02-28
                # Bu, kartın ay sonuna kadar geçerli olduğunu varsayar
                next_month = datetime.date(full_year, int(exp_month), 1).replace(day=28) + datetime.timedelta(days=4)
                expiration_date = next_month - datetime.timedelta(days=next_month.day)
                
                if expiration_date >= datetime.date.today():
                    break
                else:
                    print("❌ Kartın son kullanma tarihi geçmiş. Lütfen geçerli bir tarih girin.")
            except ValueError:
                 print("❌ Geçersiz yıl. Lütfen 4 haneli bir sayı girin (örn: 2026).")
        else:
            print("❌ Geçersiz yıl formatı. Lütfen 4 haneli bir sayı girin (örn: 2026).")
            
    while True:
        cvv = input("🔒 CVV Kodu (kartın arkasındaki 3 veya 4 haneli numara): ").strip()
        if cvv.isdigit() and 3 <= len(cvv) <= 4:
            break
        else:
            print("❌ Geçersiz CVV. Lütfen 3 veya 4 haneli bir sayı girin.")

    return {
        "card_number": card_number,
        "exp_month": exp_month,
        "exp_year": exp_year,
        "cvv": cvv
    }

if __name__ == "__main__":
    details = get_credentials_from_user()
    save_credentials(details)
