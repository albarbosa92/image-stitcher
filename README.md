# Image Stitcher

A lightweight, memory-safe Windows application designed for researchers and scientists to batch-convert, sequence, and stitch high-resolution microscopy images (SEM, optical, fluorescence) into publication-ready grid figures.

## Key Features
* **Automatic TIFF Sanitization:** Handles heavy 16-bit and multi-layer microscopy TIFFs using ImageMagick (with automatic Pillow fallback) to prevent memory crashes.
* **Multi-Folder Selection:** Add images incrementally from different folders and arrange their exact `A, B, C...` sequence before rendering.
* **Flexible Grids:** Supports any `Rows × Columns` layout, including odd numbers of panels.
* **High-Contrast Labels:** Choose between 6 label positions, 6 colors, and an optional drop shadow/stroke outline for maximum readability over noisy microstructures.
* **Publication-Ready Export:** Exports at **300 DPI** with clean white panel gutters in **PNG** (lossless), **JPEG** (95% quality, no subsampling), or **TIFF** (LZW compressed).

## Download (Windows)
No Python installation required. Go to the **[Releases](../../releases)** section and download `Image_Stitcher.exe`.

## Running from Source
1. Install Python 3.9+ and Pillow:
   ```bash
   pip install -r requirements.txt
