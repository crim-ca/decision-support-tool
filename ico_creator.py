# -*- coding: utf-8 -*-
"""
Created on Tue Jul 26 08:44:20 2022

@author: FykeJ
"""

from PIL import Image
filename = r'images/logo.png'
img = Image.open(filename)
img.save('images/logo.ico',sizes=[(64,64)])