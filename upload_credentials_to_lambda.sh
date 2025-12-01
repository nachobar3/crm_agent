#!/bin/bash
# Script para subir las credenciales de Google a Lambda

echo "🔐 Preparando credenciales para Lambda..."

# Variables - AJUSTA ESTOS VALORES
FUNCTION_NAME="tu-funcion-lambda"  # Cambia esto por el nombre de tu función Lambda
REGION="us-east-1"  # Cambia esto por tu región

# Verificar que existe el archivo de credenciales
if [ ! -f "asociate-f8e54014d9ea.json" ]; then
    echo "❌ Error: No se encuentra el archivo asociate-f8e54014d9ea.json"
    exit 1
fi

# Crear directorio temporal
mkdir -p temp_deploy
cd temp_deploy

# Copiar archivo de credenciales con el nombre correcto
cp ../asociate-f8e54014d9ea.json credentials.json

# Crear un deployment package mínimo (solo credenciales)
zip credentials.zip credentials.json

echo ""
echo "📤 Subiendo credenciales a Lambda..."
echo "   Función: $FUNCTION_NAME"
echo "   Región: $REGION"
echo ""

# Subir a Lambda
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --zip-file fileb://credentials.zip \
  --region "$REGION"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Credenciales subidas exitosamente!"
    echo ""
    echo "📝 Nota: Este comando solo subió las credenciales."
    echo "   El próximo 'git push' desplegará tu código actualizado."
else
    echo ""
    echo "❌ Error al subir credenciales"
    echo "   Verifica que tienes configurado AWS CLI y los permisos correctos"
fi

# Limpiar
cd ..
rm -rf temp_deploy

echo ""
echo "🧹 Archivos temporales eliminados"

