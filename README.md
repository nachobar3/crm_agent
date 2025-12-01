# 🤖 Nacho Leads - Telegram Bot para Gestión de Leads y Contactos

Sistema inteligente que permite gestionar una base de datos de Leads y Contactos almacenada en Google Sheets mediante un bot de Telegram con soporte para comandos de voz.

## 🌟 Características

- 🎤 **Transcripción de audio**: Envía notas de voz y el bot las transcribe automáticamente
- 🔍 **Búsquedas inteligentes**: Busca contactos por nombre, empresa o rol con fuzzy matching (ignora acentos y mayúsculas)
- ➕ **Crear contactos**: Agrega nuevos contactos a la base de datos mediante lenguaje natural
- ✏️ **Actualización de datos**: Modifica información de contactos existentes
- 📝 **Bitácora**: Registra interacciones y notas sobre cada contacto
- 🤖 **Agente de IA**: Usa GPT-4o para entender y ejecutar comandos complejos

## 📋 Estructura de la Base de Datos

La Google Sheet debe tener las siguientes columnas:

| Nombre | Teléfono | Email | Telegram | Empresa | Rol | bio | bitácora |
|--------|----------|-------|----------|---------|-----|-----|----------|
| Información del contacto | Número de teléfono | Correo electrónico | Usuario de Telegram | Empresa donde trabaja | Posición/Rol | Biografía e info personal | Registro de interacciones |

## 🚀 Instalación

### 1. Requisitos previos

- Python 3.8 o superior
- Una cuenta de Telegram y un bot creado con @BotFather
- Una cuenta de Google Cloud con acceso a Google Sheets API
- Una API key de OpenAI

### 2. Clonar o descargar el proyecto

```bash
cd nacho_leads
```

### 3. Crear entorno virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Telegram Bot Configuration
TELEGRAM_API=tu_token_de_telegram_aqui

# Google Sheets Configuration
SPREADSHEET_ID=tu_spreadsheet_id_aqui

# OpenAI API (for Whisper transcription and agent)
OPENAI_API_KEY=tu_openai_api_key_aqui
```

#### Cómo obtener cada valor:

**TELEGRAM_API:**
1. Abre Telegram y busca @BotFather
2. Envía `/newbot` y sigue las instrucciones
3. Copia el token que te proporciona

**SPREADSHEET_ID:**
1. Abre tu Google Sheet
2. El ID está en la URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
3. Copia la parte que dice `SPREADSHEET_ID`

**OPENAI_API_KEY:**
1. Ve a https://platform.openai.com/api-keys
2. Crea una nueva API key
3. Copia la key (guárdala en un lugar seguro)

### 6. Configurar Google Sheets API

**🔐 IMPORTANTE:** El archivo de credenciales de Google Cloud **NO está en el repositorio** por seguridad.

Necesitas obtener tu propio archivo JSON:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de Google Sheets
4. Crea credenciales de "Service Account"
5. Descarga el archivo JSON y guárdalo en la raíz del proyecto
6. **Importante**: Comparte tu Google Sheet con el email del service account (está en el JSON como `client_email`)

**📖 Guía detallada:** Ver [`CREDENTIALS_SETUP.md`](CREDENTIALS_SETUP.md) para instrucciones completas

## ▶️ Uso

### Opción 1: Ejecución Local (Polling Mode)

Para desarrollo o ejecución en tu máquina local:

```bash
python main.py
```

Verás un mensaje de confirmación cuando el bot esté listo:

```
🔧 Inicializando componentes...
📊 Conectando a Google Sheets...
🤖 Inicializando agente de IA...
📱 Inicializando bot de Telegram...

✅ Sistema listo!
==================================================
Bot de Leads/Contactos iniciado correctamente
==================================================

Presiona Ctrl+C para detener el bot
```

### Comandos del Bot

Abre Telegram y busca tu bot. Estos son los comandos disponibles:

**Comandos básicos:**
- `/start` - Inicia la conversación con el bot
- `/help` - Muestra la ayuda con ejemplos

**Búsquedas:**
```
Busca a Pablo Salomón
¿Quién es María García?
Muestra los contactos de Tech Corp
Lista personas con rol de CEO
Muestra todos los contactos
```

**Crear nuevos contactos:**
```
Agrega un nuevo contacto: Juan Pérez de Tech Corp
Crea un contacto para María García, trabaja en Innovation Labs como CEO
Añade a Ana Torres, su teléfono es +123456789 y es CFO de StartupXYZ
```

**Actualizaciones:**
```
Agrega a la bio de Pablo Salomón que tiene dos hijas llamadas Caia y Mirta
Actualiza el teléfono de María García a +1234567890
Actualiza el email de Juan Pérez a juan@example.com
Actualiza el telegram de Ana Torres a @anatorres
Cambia la empresa de Juan Pérez a Innovation Labs
Actualiza el rol de Ana Torres a CTO
```

**Bitácora:**
```
Añade a la bitácora de Pablo Salomón: Reunión el 27/11/2025
Registra que María García está interesada en nuestro producto
```

### 🎤 Comandos por voz

Simplemente envía una nota de voz con cualquier comando. El bot:
1. Transcribirá tu audio a texto
2. Te mostrará la transcripción
3. Ejecutará el comando
4. Te responderá con el resultado

**Ejemplo:**
*[Nota de voz]* "Agrega a la bio de Pablo Salomón que tiene dos hijas y se llaman Caia y Mirta"

El bot responderá:
```
📝 Transcripción: Agrega a la bio de Pablo Salomón que tiene dos hijas y se llaman Caia y Mirta
Bio actualizada exitosamente para Pablo Salomón
```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐
│  Telegram Bot   │
│   (Usuario)     │
└────────┬────────┘
         │
         │ Texto/Audio
         ▼
┌─────────────────┐
│  telegram_bot.py│
│  - Recibe msgs  │
│  - Transcribe   │
└────────┬────────┘
         │
         │ Texto procesado
         ▼
┌─────────────────┐
│    agent.py     │
│  - AI Agent     │
│  - Tools        │
└────────┬────────┘
         │
         │ Operaciones
         ▼
┌─────────────────┐
│sheets_manager.py│
│  - CRUD Ops     │
│  - Google API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Google Sheets  │
│   (Database)    │
└─────────────────┘
```

## 📁 Estructura de Archivos

```
nacho_leads/
│
├── main.py                          # Punto de entrada principal
├── telegram_bot.py                  # Maneja interacciones con Telegram
├── agent.py                         # Agente de IA con herramientas
├── sheets_manager.py                # Gestiona operaciones con Google Sheets
│
├── asociate-f8e54014d9ea.json      # Credenciales de Google (service account)
├── requirements.txt                 # Dependencias de Python
├── .env                            # Variables de entorno (no incluido)
└── README.md                       # Este archivo
```

## 🛠️ Componentes Principales

### 1. `sheets_manager.py`
Gestiona todas las operaciones con Google Sheets:
- Búsqueda por nombre, empresa, rol
- Actualización de campos específicos
- Lectura de todos los registros

### 2. `agent.py`
Agente de IA con las siguientes herramientas:
- `search_by_name` - Buscar por nombre (fuzzy matching)
- `search_by_company` - Buscar por empresa
- `search_by_role` - Buscar por rol
- `get_all_contacts` - Obtener todos los contactos
- `add_new_contact` - Crear nuevos contactos
- `update_bio` - Actualizar biografía
- `update_phone` - Actualizar teléfono
- `update_email` - Actualizar email
- `update_telegram` - Actualizar usuario de Telegram
- `update_company` - Actualizar empresa
- `update_role` - Actualizar rol
- `add_to_log` - Añadir a bitácora

### 3. `telegram_bot.py`
Maneja la interacción con Telegram:
- Recibe mensajes de texto
- Recibe y transcribe audio (usando Whisper de OpenAI)
- Envía respuestas al usuario

### 4. `main.py`
Punto de entrada que inicializa todos los componentes

## 🔒 Seguridad

- **No compartas** tu archivo `.env` ni tus credenciales de Google
- El archivo `.env` debe estar en `.gitignore`
- Las credenciales del service account de Google tienen acceso limitado

## 🐛 Solución de Problemas

### Error: "TELEGRAM_API not found"
- Verifica que el archivo `.env` existe y tiene el token correcto
- Asegúrate de que el archivo está en el mismo directorio que `main.py`

### Error: "Permission denied" en Google Sheets
- Verifica que has compartido la sheet con el email del service account
- El email está en `asociate-f8e54014d9ea.json` como `client_email`

### El bot no transcribe el audio
- Verifica que tu OPENAI_API_KEY es válida y tiene créditos
- Asegúrate de que estás enviando el audio en un formato compatible

### El bot no responde
- Verifica que el bot está corriendo (`python main.py`)
- Comprueba la conexión a internet
- Revisa los logs en la terminal para ver errores

## 📝 Notas Adicionales

- El bot usa GPT-4 Turbo para procesamiento de lenguaje natural
- La transcripción de audio usa Whisper de OpenAI
- Todas las respuestas son en español
- El bot mantiene contexto de conversación durante la sesión

## 🔄 Actualizaciones Futuras

Posibles mejoras:
- [x] ✅ Soporte para añadir nuevos contactos (IMPLEMENTADO)
- [x] ✅ Búsqueda fuzzy con acentos y mayúsculas (IMPLEMENTADO)
- [ ] Exportar contactos a otros formatos
- [ ] Búsquedas más complejas con filtros múltiples
- [ ] Notificaciones automáticas
- [ ] Integración con otros servicios

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias, por favor abre un issue en el repositorio o contacta al desarrollador.

## 📄 Licencia

Este proyecto es privado y de uso personal.

---

**Desarrollado con ❤️ usando Python, LangChain, y OpenAI**

