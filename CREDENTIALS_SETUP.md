# 🔐 Configuración de Credenciales

Este archivo explica cómo configurar las credenciales necesarias para el proyecto.

## ⚠️ IMPORTANTE - Seguridad

Las credenciales **NUNCA** deben subirse a GitHub. Los siguientes archivos están excluidos en `.gitignore`:
- `.env` - Variables de entorno
- `*.json` - Archivos de credenciales de Google Cloud

## 📋 Archivos de Credenciales Necesarios

### 1. Archivo `.env`

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Telegram Bot Configuration
TELEGRAM_API=tu_token_de_telegram

# Google Sheets Configuration
SPREADSHEET_ID=tu_spreadsheet_id

# OpenAI API (for Whisper transcription and agent)
OPENAI_API_KEY=tu_openai_api_key
```

**Cómo obtener cada valor:**

- **TELEGRAM_API**: 
  1. Abre Telegram y busca @BotFather
  2. Envía `/newbot` y sigue las instrucciones
  3. Copia el token que te proporciona

- **SPREADSHEET_ID**: 
  1. Abre tu Google Sheet
  2. El ID está en la URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
  3. Copia esa parte

- **OPENAI_API_KEY**: 
  1. Ve a https://platform.openai.com/api-keys
  2. Crea una nueva API key
  3. Copia la key (guárdala en un lugar seguro)

### 2. Archivo de Credenciales de Google Cloud

Necesitas un archivo JSON con las credenciales de tu Service Account de Google Cloud.

**Cómo obtenerlo:**

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto nuevo o selecciona uno existente
3. Habilita la API de Google Sheets:
   - Ve a "APIs & Services" > "Library"
   - Busca "Google Sheets API"
   - Haz clic en "Enable"
4. Crea credenciales de Service Account:
   - Ve a "APIs & Services" > "Credentials"
   - Haz clic en "Create Credentials" > "Service Account"
   - Completa el formulario y crea la cuenta
5. Descarga el archivo JSON:
   - Haz clic en la cuenta de servicio creada
   - Ve a la pestaña "Keys"
   - "Add Key" > "Create new key" > "JSON"
   - Guarda el archivo en la raíz del proyecto

**Nombre del archivo:**
Puedes usar cualquier nombre, por ejemplo: `credentials.json` o `service-account.json`

**Actualiza `main.py`** si usas un nombre diferente:
```python
credentials_file = 'tu-archivo-credenciales.json'
```

### 3. Compartir Google Sheet

**Importante:** Debes compartir tu Google Sheet con el service account:

1. Abre el archivo JSON de credenciales
2. Busca el campo `client_email` (ejemplo: `bot@proyecto.iam.gserviceaccount.com`)
3. Abre tu Google Sheet
4. Haz clic en "Compartir"
5. Agrega ese email y dale permisos de "Editor"

## 🚀 Verificación

Para verificar que todo está configurado correctamente:

```bash
# 1. Verifica que el archivo .env existe
ls -la .env

# 2. Verifica que el archivo de credenciales JSON existe
ls -la *.json

# 3. Prueba ejecutar el bot
python main.py
```

## 🔒 Buenas Prácticas de Seguridad

1. **Nunca** compartas tus credenciales
2. **Nunca** hagas commit de archivos `.env` o `.json` con credenciales
3. Si accidentalmente subes credenciales a GitHub:
   - Revoca inmediatamente esas credenciales
   - Genera nuevas credenciales
   - Usa `git filter-branch` o BFG Repo-Cleaner para limpiar el historial
4. Considera usar herramientas como:
   - [git-secrets](https://github.com/awslabs/git-secrets)
   - [detect-secrets](https://github.com/Yelp/detect-secrets)
5. Para proyectos en producción, usa servicios como:
   - AWS Secrets Manager
   - Google Secret Manager
   - HashiCorp Vault

## 📞 Ayuda

Si tienes problemas con las credenciales:
1. Verifica que los archivos existen y tienen el formato correcto
2. Verifica que el Google Sheet está compartido con el service account
3. Verifica que las APIs están habilitadas en Google Cloud
4. Revisa los logs del bot para errores específicos

