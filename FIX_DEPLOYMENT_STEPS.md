# 🔧 Cómo Arreglar el Deployment

## 📊 Lo que pasó

1. **Antes**: Tu deployment funcionaba - solo desplegaba código, las dependencias estaban en un Lambda Layer
2. **Mi cambio**: Intenté incluir todas las dependencias en el deployment package
3. **Problema**: 
   - El package se hizo muy grande
   - Intentó copiar el archivo de credenciales que no está en GitHub
4. **Solución**: Revertí al método original + necesitas actualizar tu Lambda Layer

## ✅ Pasos para Arreglar

### Paso 1: Actualizar el Lambda Layer con `pytz`

El código ahora usa `pytz` (nueva dependencia para el manejo de fechas). Necesitas actualizar tu Lambda Layer:

#### Opción A: Usando el script (más fácil)

```bash
# 1. Edita el script con los valores de tu Lambda
nano update_layer_with_pytz.sh

# Cambia estas líneas:
# LAYER_NAME="tu-layer-name"  # Pon el nombre de tu layer aquí
# REGION="us-east-1"  # Pon tu región aquí

# 2. Ejecuta el script
./update_layer_with_pytz.sh

# 3. Copia el ARN que te muestra (algo como):
# arn:aws:lambda:us-east-1:123456:layer:nombre:2

# 4. Actualiza tu función Lambda con el nuevo layer:
aws lambda update-function-configuration \
  --function-name TU_FUNCION \
  --layers arn:aws:lambda:region:account:layer:nombre:VERSION \
  --region tu-region
```

#### Opción B: Manualmente

```bash
# 1. Crear layer con dependencias
mkdir -p lambda_layer/python
pip install -r requirements.txt -t lambda_layer/python/

# 2. Crear zip
cd lambda_layer
zip -r ../lambda_layer.zip python/
cd ..

# 3. Publicar nueva versión
aws lambda publish-layer-version \
  --layer-name TU_LAYER_NAME \
  --zip-file fileb://lambda_layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region tu-region

# 4. Actualizar función con nuevo layer (usa el ARN del paso anterior)
aws lambda update-function-configuration \
  --function-name TU_FUNCION \
  --layers arn:aws:lambda:...:VERSION \
  --region tu-region

# 5. Limpiar
rm -rf lambda_layer lambda_layer.zip
```

### Paso 2: Desplegar el Código Actualizado

Una vez que el Layer esté actualizado:

```bash
git add .
git commit -m "Reverted to layer-based deployment and added datetime tool"
git push origin main
```

GitHub Actions desplegará automáticamente el código actualizado.

## 🔍 Verificar si el Layer ya tiene pytz

Antes de actualizar, puedes verificar si tu layer actual ya tiene pytz:

```bash
# Listar tus layers
aws lambda list-layers --region tu-region

# Ver una versión específica del layer
aws lambda get-layer-version \
  --layer-name TU_LAYER_NAME \
  --version-number 1 \
  --region tu-region
```

Si el layer fue creado recientemente y ya incluía todas las dependencias de requirements.txt, es posible que pytz ya esté incluido.

## 🎯 Estructura Final

```
Lambda Function:
├── Code (desde GitHub Actions):
│   ├── lambda_function.py
│   ├── agent.py
│   └── sheets_manager.py
│
└── Layers:
    ├── Layer 1: Google Credentials
    │   └── credentials.json
    │
    └── Layer 2: Python Dependencies
        └── python/
            ├── langchain/
            ├── openai/
            ├── gspread/
            ├── pytz/  ← NUEVA DEPENDENCIA
            └── ...todas las otras dependencias
```

## 📝 Notas

- El archivo de credenciales (`asociate-f8e54014d9ea.json`) debe estar en un Layer o en el environment de Lambda
- Las dependencias deben estar en un Layer separado
- Solo el código de la aplicación se despliega via GitHub Actions
- Esto mantiene el deployment rápido y ligero

## ✅ Verificar que Funciona

Después de completar los pasos:

1. Envía un mensaje al bot: "¿Qué día es hoy?"
2. Debe responder con la fecha actual
3. Prueba: "Añade a la bitácora de Juan: reunión hoy"
4. Debe guardar la fecha real en lugar de "hoy"

