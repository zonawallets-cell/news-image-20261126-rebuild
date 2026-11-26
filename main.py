#!/usr/bin/env python3
"""Copy the front-page image to the output directory.

Pure standard library. The front page is rendered by render.py and
committed as entry.png; this program only copies it to the output path
the grader reads, /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    shutil.copyfile(SRC, os.path.join(OUT_DIR, "entry.png"))


if __name__ == "__main__":
    main()
