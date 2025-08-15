import os
import subprocess
import shutil
import sys

REPO_NAME = "ktunOto"
EXE_NAME = "ktunOto.exe"
REQUIREMENTS_FILE = "requirements.txt"
ICON_NAME = "icon.ico"

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def install_deps():
    print("📦 Gerekli paketler yükleniyor...")
    run(f"pip install -r {REQUIREMENTS_FILE}")
    run("pip install pyinstaller")

def build_exe():
    print("⚙️ .exe dosyası oluşturuluyor...")
    # İkon dosyasının mevcut dizinde olduğunu varsayıyoruz
    icon_path_for_pyinstaller = ICON_NAME
    
    # Windows'ta ; Linux/macOS'ta : kullanılır. Platforma özel ayıraç.
    separator = ';' if sys.platform == 'win32' else ':'
      
    # Windows görev çubuğunda ikonun görünmesi için gerekli bayraklar
    # --windowed bayrağı konsol penceresini gizler (--noconsole ile aynı)
    # --icon bayrağı uygulamanın ikonunu belirler
    run(f"pyinstaller main.py --onefile --windowed --name {EXE_NAME} --icon={icon_path_for_pyinstaller}")
    print("✅ Derleme tamamlandı.")

def move_exe_to_root():
    src = os.path.join("dist", EXE_NAME)
    # .exe'yi installer.py'nin olduğu dizine taşıyoruz.
    dst = os.path.join(os.getcwd(), EXE_NAME)
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
    exe_full_path = os.path.join(os.getcwd(), EXE_NAME)


    vbs = f'''
    Set oWS = WScript.CreateObject("WScript.Shell")
    sLinkFile = "{shortcut_path}"
    Set oLink = oWS.CreateShortcut(sLinkFile)
    oLink.TargetPath = "{exe_full_path}"
    oLink.IconLocation = "{exe_full_path}, 0" ' .exe içindeki ilk ikonu kullan
    oLink.WindowStyle = 1
    oLink.WorkingDirectory = "{os.path.dirname(exe_full_path)}" ' Çalışma dizinini exe'nin bulunduğu dizin olarak ayarla
    oLink.Description = "KTÜN Yemekhane Otomasyon"
    oLink.Save
    '''
    # VBS script'ini installer.py'nin olduğu dizine yazalım ki os.chdir'dan etkilenmesin.
    vbs_script_path = os.path.join(os.getcwd(), "create_shortcut.vbs")
    with open(vbs_script_path, "w") as f:
        f.write(vbs.strip())

    run(f"cscript {vbs_script_path} //Nologo")
    os.remove(vbs_script_path)
    print("✅ Kısayol oluşturuldu.")

def cleanup():
    print("🧹 Geçici dosyalar temizleniyor...")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    
    spec_file = f"{EXE_NAME}.spec"
    if os.path.exists(spec_file):
        os.remove(spec_file)
    print("✅ Temizlik tamamlandı.")

def main():
    # Kullanıcının ayarlarını kaydedebilmesi için boş .env dosyası oluştur
    if not os.path.exists(".env"):
        print("📝 Boş .env dosyası oluşturuluyor...")
        with open(".env", "w") as f:
            pass # Dosyayı oluşturmak yeterli

    # İkon dosyasının varlığını kontrol et
    if not os.path.exists(ICON_NAME):
        print(f"⚠️  Uyarı: {ICON_NAME} dosyası {os.getcwd()} dizininde bulunamadı. .exe ikonsuz oluşturulacak.")
    else:
        print(f"✅ {ICON_NAME} dosyası bulundu. .exe bu ikon ile oluşturulacak.")

    install_deps()
    build_exe()
    move_exe_to_root()
    cleanup()
    
    create_shortcut()
    print(f"\n🚀 {EXE_NAME} çalıştırmaya hazır! Masaüstüne ikonlu kısayol oluşturuldu.")
    print("\n⚠️ ÖNEMLİ: Programı ilk kez çalıştırdığınızda gerekli ayarları yapmanız istenecektir.")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("❌ Bu script sadece Windows içindir.")
        sys.exit(1)
    main()
