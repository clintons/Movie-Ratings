#!/usr/bin/env python3
"""Create a placeholder poster image"""

from PIL import Image, ImageDraw, ImageFont
import os

# Create posters directory if it doesn't exist
os.makedirs('/home/claude/movie-ratings-app/posters', exist_ok=True)

# Create a simple placeholder image
img = Image.new('RGB', (300, 450), color='#f5f5f5')
draw = ImageDraw.Draw(img)

# Draw a simple frame
draw.rectangle([10, 10, 290, 440], outline='#ddd', width=2)

# Add text
text = "No Poster\nAvailable"
bbox = draw.textbbox((0, 0), text, font=None)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (300 - text_width) // 2
y = (450 - text_height) // 2
draw.text((x, y), text, fill='#999', align='center')

# Save
img.save('/home/claude/movie-ratings-app/posters/placeholder.jpg', 'JPEG')
print("Placeholder poster created!")
