#!/bin/bash
# Script para actualizar el Lambda Layer con la nueva dependencia pytz

echo "📦 Creando Lambda Layer con dependencias actualizadas..."

# Variables - AJUSTA ESTOS VALORES
LAYER_NAME="tu-layer-name"  # Cambia esto por el nombre de tu layer
REGION="us-east-1"  # Cambia esto por tu región

# Crear directorio temporal
mkdir -p lambda_layer/python

echo "📥 Instalando dependencias..."
# Instalar todas las dependencias
pip install -r requirements.txt -t lambda_layer/python/

echo "📦 Creando archivo zip..."
# Crear zip file
cd lambda_layer
zip -r ../lambda_layer.zip python/
cd ..

echo ""
echo "📤 Publicando nueva versión del Layer..."
echo "   Layer: $LAYER_NAME"
echo "   Región: $REGION"
echo ""

# Publicar nueva versión del layer
aws lambda publish-layer-version \
  --layer-name "$LAYER_NAME" \
  --zip-file fileb://lambda_layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region "$REGION"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Layer actualizado exitosamente!"
    echo ""
    echo "📝 IMPORTANTE: Copia el ARN del layer que aparece arriba"
    echo "   Formato: arn:aws:lambda:region:account:layer:nombre:VERSION"
    echo ""
    echo "🔧 Ahora actualiza tu función Lambda para usar la nueva versión:"
    echo ""
    echo "aws lambda update-function-configuration \\"
    echo "  --function-name TU_FUNCION \\"
    echo "  --layers arn:aws:lambda:region:account:layer:$LAYER_NAME:VERSION \\"
    echo "  --region $REGION"
else
    echo ""
    echo "❌ Error al publicar layer"
    echo "   Verifica que tienes configurado AWS CLI y los permisos correctos"
fi

# Limpiar
rm -rf lambda_layer lambda_layer.zip

echo ""
echo "🧹 Archivos temporales eliminados"

