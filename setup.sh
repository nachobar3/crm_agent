#!/bin/bash

# Setup script for Nacho Leads Bot

echo "🚀 Configurando Nacho Leads Bot..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
else
    echo "✅ Entorno virtual ya existe"
fi

echo ""

# Activate virtual environment
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

echo ""

# Upgrade pip
echo "⬆️  Actualizando pip..."
pip install --upgrade pip

echo ""

# Install requirements
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Archivo .env no encontrado"
    echo "📝 Creando .env desde plantilla..."
    cp env_template.txt .env
    echo ""
    echo "⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales:"
    echo "   - TELEGRAM_API"
    echo "   - SPREADSHEET_ID"
    echo "   - OPENAI_API_KEY"
    echo ""
else
    echo "✅ Archivo .env encontrado"
fi

echo ""
echo "✅ Instalación completa!"
echo ""
echo "📋 Próximos pasos:"
echo "   1. Edita el archivo .env con tus credenciales"
echo "   2. Asegúrate de compartir tu Google Sheet con el service account"
echo "   3. Ejecuta: python main.py"
echo ""
echo "Para activar el entorno virtual en el futuro, ejecuta:"
echo "   source venv/bin/activate"
echo ""

