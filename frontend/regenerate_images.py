import os
from PIL import Image

# Definisco sorgenti e destinazioni
source_dir_hgt = r"E:\sito\nownow\hgt"
source_dir_stalazio = r"E:\sito\nownow\sta lazio"
dest_dir = r"E:\sito\nownow\www.now-now.it\public\aci_fixed"

# Mappa file: nome_finale -> percorso_sorgente_completo
files_to_process = {
    "ACI-048.jpg": os.path.join(source_dir_hgt, "ACI-048.jpg"),
    "ACI-049.jpg": os.path.join(source_dir_hgt, "ACI-049.jpg"),
    "ACI-050.jpg": os.path.join(source_dir_stalazio, "ACI-050.PNG"), # Nota: PNG source
    "ACI-051.jpg": os.path.join(source_dir_hgt, "ACI-051.jpg"),
    "ACI-052.jpg": os.path.join(source_dir_hgt, "ACI-052.jpg"),
}

# Creo cartella destinazione se non esiste
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)
    print(f"Directory creata: {dest_dir}")

def process_image(src, dest):
    try:
        if not os.path.exists(src):
            print(f"❌ MANCANTE: {src}")
            return

        print(f"🔄 Processando: {src} -> {dest}")
        
        # Apro immagine
        with Image.open(src) as img:
            # Converto in RGB (rimuove alpha channel che rompe i JPG)
            rgb_img = img.convert('RGB')
            
            # Ridimensiono se troppo grande (1920px max width è standard web HD)
            max_width = 1920
            if rgb_img.width > max_width:
                ratio = max_width / float(rgb_img.width)
                new_height = int(float(rgb_img.height) * ratio)
                rgb_img = rgb_img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Salvo come JPG pulito (senza metadati extra che potrebbero corromperla)
            rgb_img.save(dest, "JPEG", quality=85, optimize=True)
            
            # Verifica finale
            if os.path.exists(dest):
                size_kb = os.path.getsize(dest) / 1024
                print(f"✅ SALVATO: {dest} ({size_kb:.2f} KB)")
            else:
                print(f"❌ ERRORE SALVATAGGIO: {dest}")

    except Exception as e:
        print(f"❌ ERRORE CRITICO su {src}: {str(e)}")

# Eseguo
for filename, source_path in files_to_process.items():
    destination_path = os.path.join(dest_dir, filename)
    process_image(source_path, destination_path)
