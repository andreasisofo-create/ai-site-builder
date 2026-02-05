import os
from PIL import Image

def optimize_single_image(src_path, dest_path):
    try:
        if not os.path.exists(src_path):
            print(f"File not found: {src_path}")
            return

        print(f"Optimizing {src_path} -> {dest_path}...")
        img = Image.open(src_path)
        
        # Convert to RGB
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # Save compressed as JPG
        img.save(dest_path, 'JPEG', quality=85, optimize=True)
        print(f"Done! New size: {os.path.getsize(dest_path)/1024:.2f} KB")
        
    except Exception as e:
        print(f"Error: {str(e)}")

src = r"E:\sito\nownow\www.now-now.it\images\services\aci\ACI-050-new.png"
dest = r"E:\sito\nownow\www.now-now.it\images\services\aci\ACI-050-final.jpg"

optimize_single_image(src, dest)
