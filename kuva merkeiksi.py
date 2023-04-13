print("Avataan...")

import os
import sys
from os.path import exists
import colorsys
from PIL import Image
import numpy
from alive_progress import alive_bar
import subprocess
import platform

# Asetetaan ohjelman polku jotenkin hienosti paikkaan mistä tiedostoa suoritetaan
os.chdir(os.path.dirname(sys.argv[0]))

print("""\nTämä ohjelma muuntaa jpg-kuvan ASCII-merkeiksi.
Jotkin muutkin tiedostotyypit toimivat ehkä, saa kokeilla. (joku png-kuva toimi mutta toiset taas ei...)
Tiedostopolku voi olla joko absoluuttinen tai suhteellinen tähän tiedostoon.
Kuvan voi siis syöttää pelkällä sen nimellä ja tiedostopäätteellä, jos se on samassa kansiossa tämän koodin kanssa.""")

# Tässä ovat symbolit kuvan piirtoa varten, niitä saa itsekin muokata
# jos pikselin valoisuus on välillä [0, 0.1[, käytetään ensimmäistä symbolia jne.
### default [[0,"@"], [0.1,"§"], [0.2,"#"], [0.3,"O"], [0.4,"¤"], [0.5,"+"], [0.6,"~"], [0.7,"-"], [0.8,"."], [0.9," "]]
### reverse [[0," "], [0.1,"."], [0.2,"-"], [0.3,"~"], [0.4,"+"], [0.5,"¤"], [0.6,"O"], [0.7,"#"], [0.8,"§"], [0.9,"@"]]
symbols = [[0,"@"], [0.1,"§"], [0.2,"#"], [0.3,"O"], [0.4,"¤"], [0.5,"+"], [0.6,"~"], [0.7,"-"], [0.8,"."], [0.9," "]]

while True:
    try:
        filename = input("\nSyötä kuvan polku: ")
        image = Image.open(filename)
        break
    except (IOError, OSError) as e:
        print("Kuvaa ei voida avata!\nVirhe: " + e)

# Luetaan kuvan pikselit
pixels = image.convert("RGB")

# Luodaan tyhjä lista (numpy array koska se on nopeampi kuin tavallinen lista)
lightness = numpy.empty(shape=(image.height, image.width), dtype=str)

# Jokaiselle pikselille toistetaan:
# Edistymispalkki
with alive_bar(image.height*image.width) as bar:
    for row in range(0, image.height):
        for column in range(0, image.width):
            rgb = pixels.getpixel((column, row))
            
            # Muunnetaan pikselin RGB-tiedot HLS-muotoon
            # huom! HLS-arvot ovat välillä 0-1
            hls = colorsys.rgb_to_hls(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            
            # Muunnetaan pikselien arvot symboleiksi
            for x in symbols:
                # käytetään vain HLS:n toista arvoa L eli lightness, kirkkaus
                if hls[1] >= x[0]:
                    lightness[row, column] = x[1]
                else:
                    break
            
            # Päivitetään edistymispalkki
            bar()

# Listat tekstiksi
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