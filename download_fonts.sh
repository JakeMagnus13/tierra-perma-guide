#!/bin/bash
# Download Google Fonts for Tierra Perma Guide
# Run once: chmod +x download_fonts.sh && ./download_fonts.sh

mkdir -p fonts

echo "Downloading Cormorant Garamond..."
curl -sL "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Regular.ttf" -o fonts/CormorantGaramond-Regular.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-SemiBold.ttf" -o fonts/CormorantGaramond-SemiBold.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Bold.ttf" -o fonts/CormorantGaramond-Bold.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/cormorantgaramond/CormorantGaramond-Italic.ttf" -o fonts/CormorantGaramond-Italic.ttf

echo "Downloading DM Sans..."
curl -sL "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans%5Bopsz%2Cwght%5D.ttf" -o fonts/DMSans-Variable.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/dmsans/DMSans-Italic%5Bopsz%2Cwght%5D.ttf" -o fonts/DMSans-Italic-Variable.ttf

echo "Downloading fallback fonts (Poppins + Lora)..."
curl -sL "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf" -o fonts/Poppins-Regular.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf" -o fonts/Poppins-Bold.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Light.ttf" -o fonts/Poppins-Light.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Medium.ttf" -o fonts/Poppins-Medium.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Italic.ttf" -o fonts/Poppins-Italic.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/lora/Lora%5Bwght%5D.ttf" -o fonts/Lora-Variable.ttf
curl -sL "https://github.com/google/fonts/raw/main/ofl/lora/Lora-Italic%5Bwght%5D.ttf" -o fonts/Lora-Italic-Variable.ttf

echo ""
echo "Done! Fonts saved to ./fonts/"
ls -la fonts/
