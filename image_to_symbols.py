print("Starting up...")

import os
import sys
from os.path import exists
import colorsys
from PIL import Image
import numpy
from alive_progress import alive_bar
import subprocess
import platform

# Setting the program's path to the path of the script or something
os.chdir(os.path.dirname(sys.argv[0]))

print("""\nThis script turns a JPG or PNG image into symbols.
Some other file types might also work, but it's pretty unstable right now even with these types :D (one PNG file worked but other didn't...)
The file path may either be absolute or relative to this file (and it can have double quotation marks around it).
In other words, the image can be inputted using only its name and file extension if it's in the same folder as this script.""")

# Here are the symbols for drawing the image, they can be changed as one wishes
# if a pixel's lightness is between [0, 0.1[, the first symbol is used, and so on...
### default [[0,"@"], [0.1,"§"], [0.2,"#"], [0.3,"O"], [0.4,"¤"], [0.5,"+"], [0.6,"~"], [0.7,"-"], [0.8,"."], [0.9," "]]
### reverse [[0," "], [0.1,"."], [0.2,"-"], [0.3,"~"], [0.4,"+"], [0.5,"¤"], [0.6,"O"], [0.7,"#"], [0.8,"§"], [0.9,"@"]]
symbols = [[0,"@"], [0.1,"§"], [0.2,"#"], [0.3,"O"], [0.4,"¤"], [0.5,"+"], [0.6,"~"], [0.7,"-"], [0.8,"."], [0.9," "]]

# The height of the symbol "█" divided by its width
# Used if you don't want the output to stretch when the aspect ratio of the symbols isn't 1:1
char_h_to_w = 112/53

# Opening the image
while True:
    try:
        filename = input("\nInput image path: ")
        # Removing quotation marks
        if (filename[0] == '"' and filename[-1] == '"'):
            filename = filename[1:-1]
        image = Image.open(filename)
        break
    except (IOError, OSError) as e:
        print("The image can't be opened!\nError:", e)

# Changing the image size
while True:
    new_width = input("\nWidth of the output (leave empty for original width): ")
    if new_width == "":
        break
    
    try:
        new_width = int(new_width)
    except ValueError as e:
        print("Invalid image size!\nError:", e)
    
    if new_width <= 0:
        print("Invalid image size!")
    
    image = image.resize((new_width, round((image.height / image.width) * new_width)))
    break

# Changing the shape of the image
if char_h_to_w != 1:
    if char_h_to_w > 1:
        ratio = (image.width, round(image.height * (1 / char_h_to_w)))
    else:
        ratio = (round(image.width * char_h_to_w), image.height)
    image = image.resize(ratio)

# Reading the pixels
pixels = image.convert("RGB")

# Creating an empty list for the pixels (numpy array because it's faster than a normal list)
lightness = numpy.empty(shape=(image.height, image.width), dtype=str)

# Repeat for every pixel:
# Progress bar
with alive_bar(image.height*image.width) as bar:
    for row in range(0, image.height):
        for column in range(0, image.width):
            rgb = pixels.getpixel((column, row))
            
            # Changing the pixels RGB-values to HLS
            # Note! HLS-values are between 0.0 and 1.0
            hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Changing the pixel values to symbols
            for x in symbols:
                # Using only the second value from HLS, lightness
                if hls[1] >= x[0]:
                    lightness[row, column] = x[1]
                else:
                    break
            
            # Updating the progress bar
            bar()

# Lists to text
lightness_txt = ""
for x in lightness:
    lightness_txt += "".join(x)+"\n"
    
print(lightness_txt)

filename_out = filename+"_ascii.txt"

if exists(filename+"_ascii.txt"):
    fileindex = 2
    while True:
        filename_out = filename+"_ascii"+str(fileindex)+".txt"
        if exists(filename_out):
            fileindex += 1
            continue
        else:
            break
        
output = open(filename_out, "w")
output.writelines(lightness_txt)
output.close()

# https://stackoverflow.com/a/435669/18611804
if platform.system() == 'Darwin':       # macOS
    subprocess.call(('open', filename_out))
elif platform.system() == 'Windows':    # Windows
    os.system(filename_out)
else:                                   # linux variants
    subprocess.call(('xdg-open', filename_out))