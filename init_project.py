#!/usr/bin/env python3
"""
🚀 CafeFlow - Proje Başlatıcı Script
Bu script proje klasör yapısını ve başlangıç dosyalarını otomatik olarak oluşturur.

Kullanım:
    python init_project.py
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Renk kodları (terminal çıktısı için)
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'

def print_header():
    """Başlık yazdır"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("  🚀 CafeFlow - Proje Başlatıcı Script")
    print("  Kurulum ve Ortam Hazırlığı")
    print("=" * 60)
    print(f"{Colors.RESET}\n")

def create_directory_structure():
    """Proje klasör yapısını oluştur"""
    print(f"{Colors.YELLOW}📁 Klasör yapısı oluşturuluyor...{Colors.RESET}")
    
    directories = [
        "src/modules",
        "src/utils",
        "src/database",
        "src/models",
        "data/backups",
        "data/exports",
        "logs",
        "tests",
        "config/.streamlit",
        "templates",
    ]
    
    for directory in directories:
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        print(f"  {Colors.GREEN}✓{Colors.RESET} {directory}/")
    
    # .gitkeep dosyaları oluştur (boş klasörleri Git'e commit etmek için)
    gitkeep_paths = [
        "data/.gitkeep",
        "logs/.gitkeep",
        "tests/.gitkeep",
    ]
    
    for gitkeep_path in gitkeep_paths:
        Path(gitkeep_path).touch()
    
    print(f"\n{Colors.GREEN}✓{Colors.RESET} Klasör yapısı başarıyla oluşturuldu.\n")

def create_placeholder_files():
    """Yer tutucu Python dosyaları oluştur"""
    print(f"{Colors.YELLOW}📄 Yer tutucu dosyaları oluşturuluyor...{Colors.RESET}")
    
    files = {
        "src/__init__.py": "# CafeFlow Package\n",
        "src/modules/__init__.py": "# Modules Package\n",
        "src/utils/__init__.py": "# Utils Package\n",
        "src/database/__init__.py": "# Database Package\n",
        "src/models/__init__.py": "# Models Package\n",
        "tests/__init__.py": "# Tests Package\n",
        "tests/test_placeholder.py": '''"""
Yer tutucu test dosyası
"""

def test_placeholder():
    """Basit test örneği"""
    assert True
''',
    }
    
    for file_path, content in files.items():
        path = Path(file_path)
        if not path.exists():
            path.write_text(content)
            print(f"  {Colors.GREEN}✓{Colors.RESET} {file_path}")
    
    print(f"\n{Colors.GREEN}✓{Colors.RESET} Yer tutucu dosyaları oluşturuldu.\n")

def create_readme():
    """README dosyası oluştur"""
    print(f"{Colors.YELLOW}📖 README.md oluşturuluyor...{Colors.RESET}")
    
    readme_content = '''
'''
    
    readme_path = Path("README.md")
    if not readme_path.exists():
        readme_path.write_text(readme_content)
        print(f"  {Colors.GREEN}✓{Colors.RESET} README.md oluşturuldu\n")
    else:
        print(f"  {Colors.YELLOW}⚠{Colors.RESET} README.md zaten var\n")

def print_summary():
    """İnisiyalizasyon özetini yazdır"""
    print(f"{Colors.BOLD}{Colors.GREEN}")
    print("=" * 60)
    print("  ✓ Proje başarıyla başlatıldı!")
    print("=" * 60)
    print(f"{Colors.RESET}\n")
    
    print(f"{Colors.BOLD}Sonraki Adımlar:{Colors.RESET}\n")
    print("1. Sanal ortamı etkinleştir:")
    print(f"   {Colors.BLUE}venv\\Scripts\\activate  # Windows{Colors.RESET}")
    print(f"   {Colors.BLUE}source venv/bin/activate  # macOS/Linux{Colors.RESET}\n")
    
    print("2. Bağımlılıkları yükle:")
    print(f"   {Colors.BLUE}pip install -r requirements.txt{Colors.RESET}\n")
    
    print("3. .env dosyasını düzenle:")
    print(f"   {Colors.BLUE}cp .env.example .env{Colors.RESET}\n")
    
    print("4. Uygulamayı başlat:")
    print(f"   {Colors.BLUE}streamlit run src/app.py{Colors.RESET}\n")
    
    print(f"📖 Daha fazla bilgi için {Colors.BOLD}SETUP.md{Colors.RESET} dosyasına bakın.\n")

def main():
    """Ana fonksiyon"""
    print_header()
    
    try:
        create_directory_structure()
        create_placeholder_files()
        create_readme()
        print_summary()
        
        print(f"{Colors.GREEN}✓ Kurulum başarıyla tamamlandı!{Colors.RESET}\n")
        return 0
        
    except Exception as e:
        print(f"\n{Colors.RED}✗ Hata oluştu: {str(e)}{Colors.RESET}\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

