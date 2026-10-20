#!/bin/bash
# Setup MockupKit – crea virtualenv e installa dipendenze
# Uso: bash setup.sh

echo "🎨 MockupKit – Setup"
echo "--------------------"

python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "✅ Pronto! Per iniziare:"
echo "   source .venv/bin/activate"
echo "   python genera_immagini.py --config config/ITA.yaml"
