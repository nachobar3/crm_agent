# 🔐 Cómo Manejar Credenciales de Google en AWS Lambda

## ⚠️ Problema
El archivo `asociate-f8e54014d9ea.json` contiene credenciales sensibles y **NO debe estar en GitHub**.

## ✅ Soluciones

### Opción 1: Subir el archivo manualmente a Lambda (RECOMENDADO)

#### Paso 1: Crear un paquete con las credenciales

```bash
# En tu máquina local
cd /home/ignacio/CodeProjects/nacho_leads

# Crear directorio temporal
mkdir -p temp_credentials

# Copiar solo el archivo de credenciales
cp asociate-f8e54014d9ea.json temp_credentials/credentials.json

# Crear zip
cd temp_credentials
zip -r ../credentials_layer.zip credentials.json
cd ..
```

#### Paso 2: Subir a Lambda como Layer

```bash
# Crear un Lambda Layer con las credenciales
aws lambda publish-layer-version \
  --layer-name google-credentials \
  --zip-file fileb://credentials_layer.zip \
  --compatible-runtimes python3.11 python3.12 \
  --region tu-region

# Esto te dará un ARN como:
# arn:aws:lambda:region:account-id:layer:google-credentials:1
```

#### Paso 3: Adjuntar el Layer a tu función Lambda

```bash
# Obtener el ARN del layer del comando anterior y usarlo aquí
aws lambda update-function-configuration \
  --function-name tu-funcion-lambda \
  --layers arn:aws:lambda:region:account-id:layer:google-credentials:1 \
  --region tu-region
```

#### Paso 4: Actualizar lambda_function.py

El código ya está configurado para buscar `credentials.json` por defecto:

```python
credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
```

### Opción 2: Usar AWS Secrets Manager (Más seguro pero más complejo)

#### Paso 1: Subir credenciales a Secrets Manager

```bash
aws secretsmanager create-secret \
  --name google-sheets-credentials \
  --secret-string file://asociate-f8e54014d9ea.json \
  --region tu-region
```

#### Paso 2: Dar permisos a Lambda

Agregar esta política al rol de Lambda:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": "arn:aws:secretsmanager:region:account:secret:google-sheets-credentials-*"
    }
  ]
}
```

#### Paso 3: Modificar el código Lambda

Necesitarías modificar `sheets_manager.py` para leer de Secrets Manager.

---

## 🚀 Método Rápido: Incluir en el Deployment (Solo para Testing)

⚠️ **NO RECOMENDADO PARA PRODUCCIÓN**

Si quieres incluir las credenciales en el deployment (temporal):

1. **Asegúrate de que el archivo esté en .gitignore**:
```bash
echo "asociate-f8e54014d9ea.json" >> .gitignore
```

2. **Sube las credenciales usando AWS CLI directamente**:

```bash
# Crear deployment con credenciales
mkdir -p build
pip install -r requirements.txt -t build/
cp lambda_function.py agent.py sheets_manager.py build/
cp asociate-f8e54014d9ea.json build/credentials.json

cd build
zip -r ../deployment_with_creds.zip .
cd ..

# Subir a Lambda
aws lambda update-function-code \
  --function-name tu-funcion-lambda \
  --zip-file fileb://deployment_with_creds.zip \
  --region tu-region

# Limpiar
rm -rf build deployment_with_creds.zip
```

---

## 📋 Estado Actual

Después de mi cambio:
- ✅ GitHub Actions despliega el código y dependencias
- ❌ Las credenciales NO se incluyen (por seguridad)
- 🔧 Necesitas configurar las credenciales en Lambda usando una de las opciones arriba

## 🎯 Recomendación

**Para desarrollo rápido:** Usa la Opción 1 (Lambda Layer)
**Para producción:** Usa la Opción 2 (Secrets Manager)

## ✅ Verificar que funciona

Después de configurar las credenciales:

```bash
# Hacer un push para desplegar el código
git add .
git commit -m "Fixed deployment - credentials handled separately"
git push origin main

# El deployment ahora debería funcionar
```

Luego prueba el bot en Telegram.

