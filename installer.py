import os
import subprocess
import shutil
import sys

REPO_URL = "https://github.com/c4kar/ktunOto"
REPO_NAME = "ktunOto"
EXE_NAME = "ktunOto.exe"
REQUIREMENTS_FILE = "requirements.txt"
ICON_NAME = "icon.ico"

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def clone_repo():
    if not os.path.exists(REPO_NAME):
        print("📥 Repo klonlanıyor...")
        run(f"git clone {REPO_URL}")
    else:
        print("✅ Repo zaten klonlanmış.")

def install_deps():
    print("📦 Gerekli paketler yükleniyor...")
    run(f"pip install -r {os.path.join(os.getcwd(), REQUIREMENTS_FILE)}")
    run("pip install pyinstaller")

def build_exe():
    print("⚙️ .exe dosyası oluşturuluyor...")
    # İkon dosyasının, klonlanan repo içinde olduğunu varsayıyoruz.
    # pyinstaller çalıştırıldığında cwd zaten REPO_NAME içinde olacak.
    icon_path_for_pyinstaller = ICON_NAME
    run(f"pyinstaller main.py --onefile --noconsole --name {EXE_NAME} --icon={icon_path_for_pyinstaller}")
    print("✅ Derleme tamamlandı.")

def move_exe_to_root():
    src = os.path.join("dist", EXE_NAME)
    # .exe'yi installer.py'nin olduğu dizine taşıyoruz.
    # os.getcwd() burada installer.py'nin olduğu dizini değil, REPO_NAME dizinini gösterir.
    # Bu yüzden bir üst dizine çıkmamız gerekiyor.
    dst = os.path.join(os.path.dirname(os.getcwd()), EXE_NAME)
    if os.path.exists(src):
        shutil.move(src, dst)
        print(f"📦 {EXE_NAME} ana dizine taşındı.")

    else:
        print("❌ .exe bulunamadı!")

def create_shortcut():
    print("📌 Masaüstüne kısayol oluşturuluyor...")
    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    shortcut_path = os.path.join(desktop, f"{REPO_NAME}.lnk")
    
    # Kısayolun hedefi olan .exe dosyasının tam yolu
    # move_exe_to_root sonrasında .exe, installer.py'nin olduğu dizinde olacak.
    # os.getcwd() burada REPO_NAME dizinini gösteriyor.
    # Bu yüzden bir üst dizine (installer.py'nin olduğu yere) referans vermeliyiz.
    exe_full_path = os.path.join(os.path.dirname(os.getcwd()), EXE_NAME)


    vbs = f'''
Set oWS = WScript.CreateObject("WScript.Shell")
sLinkFile = "{shortcut_path}"
Set oLink = oWS.CreateShortcut(sLinkFile)
oLink.TargetPath = "{exe_full_path}"
oLink.IconLocation = "{exe_full_path}, 0" ' .exe içindeki ilk ikonu kullan
oLink.WindowStyle = 1
oLink.Description = "KTÜN Yemekhane Otomasyon"
oLink.Save
'''
    # VBS script'ini installer.py'nin olduğu dizine yazalım ki os.chdir'dan etkilenmesin.
    vbs_script_path = os.path.join(os.path.dirname(os.getcwd()), "create_shortcut.vbs")
    with open(vbs_script_path, "w") as f:
        f.write(vbs.strip())

    run(f"cscript {vbs_script_path} //Nologo")
    os.remove(vbs_script_path)
    print("✅ Kısayol oluşturuldu.")

def main():
    installer_script_dir = os.getcwd() # Başlangıç dizinini kaydet
    clone_repo()
    os.chdir(REPO_NAME) # Klonlanan repo dizinine geç
    
    # İkon dosyasının varlığını kontrol et (isteğe bağlı ama iyi bir pratik)
    if not os.path.exists(ICON_NAME):
        print(f"⚠️  Uyarı: {ICON_NAME} dosyası {os.getcwd()} dizininde bulunamadı. .exe ikonsuz oluşturulacak.")

    install_deps()
    build_exe()
    move_exe_to_root() # Bu fonksiyon içinde cwd hala REPO_NAME

    # create_shortcut ve sonraki işlemler için ana dizine (installer.py'nin olduğu yere) dön
    os.chdir(installer_script_dir)
    
    create_shortcut()
    print(f"\n🚀 {EXE_NAME} çalıştırmaya hazır! Masaüstüne ikonlu kısayol oluşturuldu.")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("❌ Bu script sadece Windows içindir.")
        sys.exit(1)
    main()
