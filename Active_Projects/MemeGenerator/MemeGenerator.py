# Import the modules
from PIL import Image, ImageDraw, ImageFont
import textwrap

# Define the image file name
image_file = "dog.jpg"

# Define the text to add to the image
text = "This is fine"

# Define the font file name and size
font_file = "impact.ttf"
font_size = 40

# Define the text color and outline color
text_color = "white"
outline_color = "black"

# Define the text margin and width
text_margin = 10
text_width = 300

# Open the image file
image = Image.open(image_file)

# Create an image draw object
draw = ImageDraw.Draw(image)

# Create a font object
font = ImageFont.truetype(font_file, font_size)

# Wrap the text to fit the text width
lines = textwrap.wrap(text, width=text_width // font_size)

# Calculate the text height
text_height = font_size * len(lines) + text_margin * (len(lines) - 1)

# Calculate the text position
x = (image.width - text_width) // 2
y = image.height - text_height - text_margin

# Loop through the lines
for line in lines:
    # Draw the text with an outline
    draw.text((x - 1, y), line, font=font, fill=outline_color)
    draw.text((x + 1, y), line, font=font, fill=outline_color)
    draw.text((x, y - 1), line, font=font, fill=outline_color)
    draw.text((x, y + 1), line, font=font, fill=outline_color)
    draw.text((x, y), line, font=font, fill=text_color)
    # Update the y position
    y += font_size + text_margin

# Save the image as a file
image.save("meme.jpg")
