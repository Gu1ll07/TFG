from PIL import Image
import os

def resize_image_keep_aspect(input_path, output_path, max_width, max_height):
    if not os.path.exists(input_path):
        print(f"Error: El archivo '{input_path}' no existe.")
        return
    with Image.open(input_path) as img:
        img.thumbnail((max_width, max_height), Image.LANCZOS)
        img.save(output_path, quality=95, optimize=True)

# Ejemplo de uso:
# resize_image_keep_aspect('3.png', 'output.png', 1920, 1080)

if __name__ == "__main__":
    resize_image_keep_aspect('3.png', 'output.png', 1920, 1080)