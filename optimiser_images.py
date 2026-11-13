#!/usr/bin/env python3
"""Reduit les photos trop lourdes du dossier public/ (max 1600 px de large).
Prerequis : pip install pillow      Usage : python optimiser_images.py
Les originaux sont copies dans public_originaux/ avant d'etre reduits."""
import os, shutil
from PIL import Image, ImageOps
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'public'); BAK = os.path.join(ROOT, 'public_originaux')
for d, _, files in os.walk(SRC):
    for f in files:
        if not f.lower().endswith(('.jpg', '.jpeg', '.png')): continue
        p = os.path.join(d, f)
        if os.path.getsize(p) < 600_000: continue
        b = os.path.join(BAK, os.path.relpath(p, SRC)); os.makedirs(os.path.dirname(b), exist_ok=True)
        if not os.path.exists(b): shutil.copy2(p, b)
        im = ImageOps.exif_transpose(Image.open(b))
        if im.width > 1600: im = im.resize((1600, int(im.height * 1600 / im.width)), Image.LANCZOS)
        if f.lower().endswith('.png'): im.save(p, optimize=True)
        else: im.convert('RGB').save(p, quality=82, optimize=True)
        print(f, round(os.path.getsize(b)/1e6, 1), 'Mo ->', round(os.path.getsize(p)/1e6, 2), 'Mo')
print('Termine.')
