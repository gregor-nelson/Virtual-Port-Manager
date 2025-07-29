"""
Simple SVG-inspired ICO converter for PyInstaller builds
Creates an icon based on the app_icon.svg design without external dependencies
Requires only: pip install pillow
"""

from PIL import Image, ImageDraw
import math
import os

def create_icon_from_svg_design(ico_path):
    """Create an icon based on the app_icon.svg design"""
    sizes = [16, 24, 32, 48, 64, 128, 256]
    images = []
    
    print(f"Creating icon based on SVG design at {ico_path}")
    
    for size in sizes:
        # Create transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center = size // 2
        
        # Colors from the SVG
        line_color = (0, 188, 242, 255)  # #00BCF2
        hub_color_1 = (0, 120, 212, 255)  # #0078D4
        hub_color_2 = (0, 90, 158, 255)   # #005A9E
        white_color = (255, 255, 255, 255)
        connector_pin_color = (0, 90, 158, 200)
        
        # Scale factors
        connection_length = int(size * 0.44)
        endpoint_radius = max(1, int(size * 0.06))
        hub_size = max(4, int(size * 0.25))
        
        # Draw 6 connection lines radiating from center
        for i in range(6):
            angle = i * math.pi / 3
            x2 = center + connection_length * math.cos(angle)
            y2 = center + connection_length * math.sin(angle)
            
            # Draw line
            line_width = max(1, size//20)
            draw.line([center, center, x2, y2], fill=line_color, width=line_width)
            
            # Draw endpoint circles
            draw.ellipse([x2-endpoint_radius, y2-endpoint_radius, 
                         x2+endpoint_radius, y2+endpoint_radius], 
                        fill=line_color)
        
        # Draw central hexagonal hub
        hub_points = []
        hub_radius = hub_size
        for i in range(6):
            angle = i * math.pi / 3
            x = center + hub_radius * math.cos(angle)
            y = center + hub_radius * math.sin(angle)
            hub_points.extend([x, y])
        
        # Draw hub with gradient-like effect (darker outer, lighter inner)
        draw.polygon(hub_points, fill=hub_color_2, outline=hub_color_1)
        
        # Draw inner highlight
        if size >= 24:
            inner_points = []
            inner_radius = hub_radius * 0.7
            for i in range(6):
                angle = i * math.pi / 3
                x = center + inner_radius * math.cos(angle)
                y = center + inner_radius * math.sin(angle)
                inner_points.extend([x, y])
            draw.polygon(inner_points, fill=hub_color_1)
        
        # Draw serial port connector inside hub
        if size >= 16:
            conn_width = max(2, int(size * 0.15))
            conn_height = max(1, int(size * 0.09))
            conn_x = center - conn_width//2
            conn_y = center - conn_height//2
            
            # White connector body
            draw.rectangle([conn_x, conn_y, conn_x+conn_width, conn_y+conn_height], 
                          fill=white_color, outline=connector_pin_color)
            
            # Draw connector pins if size is large enough
            if size >= 32:
                pin_size = max(1, size//64)
                pins_per_row = 4
                pin_spacing = conn_width // (pins_per_row + 1)
                
                for row in range(2):
                    for col in range(pins_per_row):
                        pin_x = conn_x + pin_spacing * (col + 1) - pin_size//2
                        pin_y = conn_y + (conn_height//3) * (row + 1) - pin_size//2
                        draw.ellipse([pin_x, pin_y, pin_x+pin_size, pin_y+pin_size], 
                                   fill=connector_pin_color)
        
        images.append(img)
        print(f"  Generated {size}x{size} icon")
    
    # Save as ICO with all sizes
    images[0].save(ico_path, format='ICO', 
                   sizes=[(img.width, img.height) for img in images])
    print(f"✅ Successfully created ICO at {ico_path}")
    return True

if __name__ == "__main__":
    ico_file = "app_icon.ico"
    
    # Check if running from assets/icons directory
    if os.path.basename(os.getcwd()) == "icons":
        create_icon_from_svg_design(ico_file)
    else:
        # Running from project root
        create_icon_from_svg_design(f"assets/icons/{ico_file}")