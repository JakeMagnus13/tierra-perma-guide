# Tierra Perma — Tropical Home Design Guide PDF Builder

Generates the designed PDF for the Tierra Perma Tropical Home Design Guide.

## Quick Start

```bash
# 1. Clone and enter the repo
git clone <your-repo-url>
cd tierra-perma-guide

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download fonts (run once)
chmod +x download_fonts.sh
./download_fonts.sh

# 4. Add your images to the images/ folder (see structure below)

# 5. Build the PDF
python3 build_guide.py

# Output: output/Tierra-Perma-Tropical-Home-Design-Guide.pdf
```

## Folder Structure

```
tierra-perma-guide/
  build_guide.py              # Main build script
  download_fonts.sh           # Font downloader
  requirements.txt            # Python dependencies
  README.md                   # This file
  fonts/                      # Auto-populated by download_fonts.sh
  images/
    diagrams/
      D1-site-reading.png     # Site analysis diagram
      D2-orientation.png      # Orientation plan view
      D3-ventilation.png      # Cross-ventilation section
      D4-roof-detail.png      # Ventilated roof assembly
      D5-shading.png          # Shading comparison
      D6-wall-sections.png    # Material wall sections
      D7-site-systems.png     # Integrated site systems (isometric)
    visuals/
      A1-rainfall-chart.png   # Guanacaste annual rainfall
      A5-ac-cost-infographic.png  # AC cost comparison
      cover.png               # Cover illustration
      back-cover.png          # Back cover / CTA illustration
      material-texture-strip.png  # Material texture banner
    photography/              # Optional — add as you shoot
      P1-concrete-block.jpg
      P3-raw-site.jpg
      P4-passive-interior.jpg
      P5-timber.jpg
      P6-bamboo.jpg
      P7-stone.jpg
      P8-earth.jpg
      P9-rainwater.jpg
      P10-food-forest.jpg
      P11-solar.jpg
      P12-landscape.jpg
      P13-indoor-outdoor.jpg
    brand/
      logo.png                # Tierra Perma logo (optional)
  output/                     # Generated PDF appears here
```

## Image Notes

- The script will use placeholder boxes for any missing images
- Supports .png, .jpg, .jpeg, .webp, .tiff
- Images are auto-fitted to their layout slots preserving aspect ratio
- For best quality, use images at least 2400px wide for full-width slots
- Diagrams and visuals from AI generation should be saved at highest available resolution

## Fonts

The script uses Cormorant Garamond (headings) and DM Sans (body) — the Tierra Perma brand fonts. If these aren't available, it falls back to Lora and Poppins, then to Helvetica.

Run `download_fonts.sh` once to get all fonts.

## Customisation

- **Contact details**: Edit the `build_section_10()` function to update email, website, phone
- **Content edits**: Each section is a separate function — edit text directly in the function
- **Layout tweaks**: Adjust `MARGIN_L`, `MARGIN_R`, `MARGIN_T`, `MARGIN_B` at the top
- **Colours**: All brand colours are defined as constants at the top of the script
