from PIL import Image
import sys
img='mitie_logo.png'
try:
    im=Image.open(img)
    print('OK', im.format, im.size)
except Exception as e:
    print('ERR', e)
