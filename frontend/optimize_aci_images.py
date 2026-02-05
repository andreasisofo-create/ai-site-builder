import os
from PIL import Image

def optimize_image(path):
    try:
        if not os.path.exists(path):
            print(f"File not found: {path}")
            return

        print(f"Optimizing {path}...")
        img = Image.open(path)
        
        # Convert to RGB (in case of RGBA/PNG)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too huge (max width 1920)
        max_width = 1920
        if img.width > max_width:
            ratio = max_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
        # Save compressed
        img.save(path, 'JPEG', quality=85, optimize=True)
        print(f"Done: {path} - New size: {os.path.getsize(path)/1024:.2f} KB")
        
    except Exception as e:
        print(f"Error optimizing {path}: {str(e)}")

# Use absolute path to the images
base_path = r"E:\sito\nownow\www.now-now.it\images\services\aci"
files = [
    "ACI-048-final.jpg",
    "ACI-049-final.jpg",
    "ACI-051-final.jpg",
    "ACI-052-final.jpg"
]

for f in files:
    optimize_image(os.path.join(base_path, f))
