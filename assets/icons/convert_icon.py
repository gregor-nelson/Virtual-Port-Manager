"""
SVG to ICO converter for PyInstaller builds
Requires: pip install pillow
Optional: pip install cairosvg (for better SVG rendering)
"""

from PIL import Image
import io
import os

try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False

def convert_svg_to_ico(svg_path, ico_path):
    """Convert SVG to ICO format with multiple sizes"""
    if not os.path.exists(svg_path):
        print(f"Error: SVG file not found at {svg_path}")
        return False
    
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    print(f"Converting {svg_path} to {ico_path}")
    
    if HAS_CAIROSVG:
        try:
            for size in sizes:
                # Convert SVG to PNG bytes at specific size
                png_bytes = cairosvg.svg2png(
                    url=svg_path,
                    output_width=size,
                    output_height=size
                )
                
                # Load PNG bytes into PIL Image
                img = Image.open(io.BytesIO(png_bytes))
                
                # Ensure RGBA mode for transparency
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                images.append(img)
                print(f"  Generated {size}x{size} icon")
            
            # Save as ICO with all sizes
            images[0].save(
                ico_path, 
                format='ICO', 
                sizes=[(img.width, img.height) for img in images]
            )
            
            print(f"✅ Successfully created ICO at {ico_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error converting SVG: {e}")
            print("Falling back to enhanced icon generation...")
            return create_fallback_ico(ico_path)
    else:
        print("❌ cairosvg not available. Using enhanced fallback icon generation...")
        return create_fallback_ico(ico_path)

def create_fallback_ico(ico_path):
    """Create a fallback icon if SVG conversion fails"""
    from PIL import ImageDraw
    
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    print("Creating fallback icon...")
    
    for size in sizes:
        # Create transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw blue gradient-like hub (hexagonal shape approximation)
        center = size // 2
        radius = int(size * 0.35)
        
        # Draw hexagonal hub
        points = []
        import math
        for i in range(6):
            angle = i * math.pi / 3
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.extend([x, y])
        
        draw.polygon(points, fill=(0, 120, 212, 255), outline=(0, 90, 158, 255))
        
        # Draw connection lines
        line_length = int(size * 0.4)
        for i in range(6):
            angle = i * math.pi / 3
            x1 = center + radius * 0.8 * math.cos(angle)
            y1 = center + radius * 0.8 * math.sin(angle)
            x2 = center + line_length * math.cos(angle)
            y2 = center + line_length * math.sin(angle)
            draw.line([x1, y1, x2, y2], fill=(0, 188, 242, 255), width=max(1, size//20))
            
            # Draw endpoint circles
            endpoint_radius = max(1, size//16)
            draw.ellipse([x2-endpoint_radius, y2-endpoint_radius, 
                         x2+endpoint_radius, y2+endpoint_radius], 
                        fill=(0, 188, 242, 255))
        
        # Draw serial connector inside hub
        if size >= 24:
            conn_width = max(4, size//6)
            conn_height = max(2, size//10)
            conn_x = center - conn_width//2
            conn_y = center - conn_height//2
            draw.rectangle([conn_x, conn_y, conn_x+conn_width, conn_y+conn_height], 
                          fill=(255, 255, 255, 255), outline=(0, 90, 158, 128))
        
        images.append(img)
    
    # Save as ICO
    images[0].save(ico_path, format='ICO', 
                   sizes=[(img.width, img.height) for img in images])
    print(f"✅ Created fallback ICO at {ico_path}")
    return True

if __name__ == "__main__":
    svg_file = "app_icon.svg"
    ico_file = "app_icon.ico"
    
    # Check if running from assets/icons directory
    if os.path.basename(os.getcwd()) == "icons":
        convert_svg_to_ico(svg_file, ico_file)
    else:
        # Running from project root
        convert_svg_to_ico(f"assets/icons/{svg_file}", f"assets/icons/{ico_file}")