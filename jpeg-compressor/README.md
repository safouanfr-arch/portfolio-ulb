# JPEG Compressor

A Bash utility from the ULB INFO-F-201 course that rotates JPEGs according to their metadata, downsizes them to fit within a square, and re-encodes them at quality 85. It processes a single picture or a directory.

## Run

Requires Bash, GNU core utilities and find, and ImageMagick on Linux or WSL. It accepts ImageMagick 7 (`magick`) and ImageMagick 6 (`convert`).

```sh
bash compress_jpg.sh 1200 "photos/holiday photo.jpg"
bash compress_jpg.sh --recursive --strip --ext jpeg 800 photos/
python3 test_compressor.py
```

`--recursive` visits subdirectories. `--strip` removes metadata. `--ext` chooses the output extension. Images smaller than the target are re-encoded at their original dimensions. The output is written beside the source, for example `holiday photo.compressed.jpg`. Existing files are preserved and previously generated copies are skipped during directory scans. Output directories must support hard links.

The portfolio edition retains the original options and makes the output non-destructive.
