import os
import glob
from PIL import Image, ImageDraw, ImageFont
import math

def get_file_size_str(filepath):
    size_bytes = os.path.getsize(filepath)
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"

def create_collage(original_path, output_dir, recon_dir):
    filename = os.path.basename(original_path)
    name_no_ext = os.path.splitext(filename)[0]
    
    # Find reconstructed files
    # Pattern: {filename}_q{qp}.png
    pattern = os.path.join(recon_dir, f"{filename}_q*.png")
    recon_files = glob.glob(pattern)
    
    if not recon_files:
        print(f"No reconstructed files found for {filename}")
        return

    # Sort by QP (extract QP from filename)
    # filename_q12.png -> 12
    def get_qp(path):
        try:
            part = path.split('_q')[-1]
            qp = int(part.split('.')[0])
            return qp
        except:
            return 999

    recon_files.sort(key=get_qp)
    
    # We expect 3 reconstructed images. 
    # If more, take 3 representative ones (Low, Mid, High QP)
    # If fewer, use what we have.
    
    # Layout:
    # Original | QP Low (High Quality)
    # --------------------------------
    # QP Mid   | QP High (Low Quality)
    
    images_to_show = []
    
    # 1. Original
    images_to_show.append({
        'path': original_path,
        'label': f"Original\n{get_file_size_str(original_path)}",
        'type': 'original'
    })
    
    # 2. Reconstructed
    for recon_path in recon_files:
        qp = get_qp(recon_path)
        # Fix: replace only the extension
        bin_path = os.path.splitext(recon_path)[0] + '.bin'
        bin_size = get_file_size_str(bin_path) if os.path.exists(bin_path) else "N/A"
        
        images_to_show.append({
            'path': recon_path,
            'label': f"QP {qp}\nBin: {bin_size}",
            'type': 'recon'
        })
        
    # Ensure we have 4 images for 2x2 grid
    # If we have more than 3 recon, pick 3.
    if len(images_to_show) > 4:
        # Keep Original, and 3 recon (First, Middle, Last)
        recon_subset = [images_to_show[1], images_to_show[len(images_to_show)//2], images_to_show[-1]]
        images_to_show = [images_to_show[0]] + recon_subset
    
    # Load images
    loaded_images = []
    for item in images_to_show:
        img = Image.open(item['path'])
        loaded_images.append({'img': img, 'label': item['label']})
        
    # Resize for collage if too big
    # Target width for single image in grid
    target_w = 1920 // 2
    
    resized_images = []
    for item in loaded_images:
        img = item['img']
        aspect = img.height / img.width
        target_h = int(target_w * aspect)
        img_resized = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        resized_images.append({'img': img_resized, 'label': item['label']})
        
    # Create canvas
    grid_w = target_w * 2
    grid_h = resized_images[0]['img'].height * 2 # Assuming all have same aspect ratio
    
    collage = Image.new('RGB', (grid_w, grid_h), (255, 255, 255))
    draw = ImageDraw.Draw(collage)
    
    # Try to load a font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    positions = [(0, 0), (target_w, 0), (0, resized_images[0]['img'].height), (target_w, resized_images[0]['img'].height)]
    
    for i, item in enumerate(resized_images):
        if i >= 4: break
        img = item['img']
        pos = positions[i]
        collage.paste(img, pos)
        
        # Draw label with background
        label = item['label']
        text_bbox = draw.textbbox((0, 0), label, font=font)
        text_w = text_bbox[2] - text_bbox[0]
        text_h = text_bbox[3] - text_bbox[1]
        
        x = pos[0] + 20
        y = pos[1] + 20
        
        # Semi-transparent background
        # PIL doesn't support alpha drawing on RGB directly easily without composite
        # So just draw a black rectangle
        draw.rectangle((x - 10, y - 10, x + text_w + 10, y + text_h + 10), fill="black")
        draw.text((x, y), label, font=font, fill="white")

    output_path = os.path.join(output_dir, f"collage_{name_no_ext}.jpg")
    collage.save(output_path, quality=90)
    print(f"Saved collage to {output_path}")

def main():
    original_dir = "media/data/my_image_test"
    recon_dir = "out_bin/image_test/MyImage"
    output_dir = "test_results/collages"
    
    os.makedirs(output_dir, exist_ok=True)
    
    original_files = glob.glob(os.path.join(original_dir, "*.png"))
    
    for orig_path in original_files:
        create_collage(orig_path, output_dir, recon_dir)

if __name__ == "__main__":
    main()
