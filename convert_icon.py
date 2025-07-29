"""
Simple script to convert SVG to ICO format for PyInstaller builds
Requires: pip install pillow
"""

from PIL import Image, ImageDraw
import xml.etree.ElementTree as ET
import re

def create_simple_ico(svg_path, ico_path):
    """Create a simple blue icon from SVG dimensions"""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    for size in sizes:
        # Create a simple blue icon with white center
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw blue circle background
        margin = size // 8
        draw.ellipse([margin, margin, size-margin, size-margin], 
                    fill=(0, 120, 212, 255))
        
        # Draw white center rectangle (representing serial port)
        center = size // 2
        rect_size = size // 4
        draw.rectangle([center - rect_size//2, center - rect_size//2,
                       center + rect_size//2, center + rect_size//2],
                      fill=(255, 255, 255, 255))
        
        images.append(img)
    
    # Save as ICO
    images[0].save(ico_path, format='ICO', 
                   sizes=[(img.width, img.height) for img in images])
    print(f"Created simple ICO at {ico_path}")

if __name__ == "__main__":
    create_simple_ico("assets/icons/app_icon.svg", "assets/icons/app_icon.ico")