"""
AWS Lambda Handler for Telegram Bot with Webhooks
Handles incoming Telegram updates via API Gateway
"""

import json
import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from openai import OpenAI
from sheets_manager import SheetsManager
from agent import LeadsAgent


# Initialize components globally for Lambda warm starts
sheets_manager = None
agent = None
openai_client = None
application = None


def initialize_components():
    """Initialize all components (runs once per cold start)"""
    global sheets_manager, agent, openai_client, application
    
    if sheets_manager is None:
        print("🔧 Initializing components...")
        
        # Get environment variables
        telegram_token = os.getenv('TELEGRAM_API')
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        credentials_file = os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json')
        
        # Validate environment variables
        if not all([telegram_token, spreadsheet_id, openai_api_key]):
            raise ValueError("Missing required environment variables")
        
        # Initialize Google Sheets Manager
        print("📊 Connecting to Google Sheets...")
        sheets_manager = SheetsManager(credentials_file, spreadsheet_id)
        
        # Initialize AI Agent
        print("🤖 Initializing AI agent...")
        agent = LeadsAgent(sheets_manager, openai_api_key)
        
        # Initialize OpenAI client
        openai_client = OpenAI(api_key=openai_api_key)
        
        # Initialize Telegram Application
        print("📱 Initializing Telegram application...")
        application = Application.builder().token(telegram_token).build()
        
        # Add handlers
        setup_handlers(application)
        
        print("✅ Components initialized successfully")


def setup_handlers(app):
    """Setup message handlers"""
    
    async def start_command(update: Update, context):
        """Handle /start command"""
        welcome_message = """
¡Hola! 👋

Soy tu asistente de Leads y Contactos. Puedo ayudarte a:

📋 Buscar contactos por nombre, empresa o rol
➕ Crear nuevos contactos
✏️ Actualizar información de contactos
📝 Añadir notas a la bitácora
🎤 Procesar comandos por voz

Ejemplos:
- "Busca a Pablo Salomón"
- "Agrega un nuevo contacto: Juan Pérez de Tech Corp"
- "Actualiza el teléfono de María García a +1234567890"

Usa /help para ver más ejemplos.
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(update: Update, context):
        """Handle /help command"""
        help_message = """
📚 Comandos y ejemplos:

🔍 BÚSQUEDAS:
• "Busca a [nombre]"
• "Muestra los contactos de [empresa]"
• "Lista personas con rol de [rol]"

➕ CREAR CONTACTOS:
• "Agrega un nuevo contacto: [nombre]"
• "Crea contacto para [nombre] de [empresa]"

✏️ ACTUALIZACIONES:
• "Agrega a la bio de [nombre] que [info]"
• "Actualiza el teléfono de [nombre] a [número]"
• "Actualiza el email de [nombre] a [email]"
• "Actualiza el telegram de [nombre] a [usuario]"

📝 BITÁCORA:
• "Añade a la bitácora de [nombre]: [nota]"

🎤 Puedes usar notas de voz para cualquier comando!
        """
        await update.message.reply_text(help_message)
    
    async def handle_text(update: Update, context):
        """Handle text messages"""
        user_message = update.message.text
        
        # Process with agent
        response = agent.process_query(user_message)
        
        # Send response
        await update.message.reply_text(response)
    
    async def handle_voice(update: Update, context):
        """Handle voice messages"""
        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_audio:
                temp_path = temp_audio.name
                await voice_file.download_to_drive(temp_path)
            
            # Transcribe audio
            with open(temp_path, 'rb') as audio_file:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Process with agent
            transcribed_text = transcript.text
            response = agent.process_query(transcribed_text)
            
            # Send single combined response
            combined_response = f"📝 Transcripción: {transcribed_text}\n\n{response}"
            await update.message.reply_text(combined_response)
            
        except Exception as e:
            error_message = f"❌ Error: {str(e)}"
            try:
                await update.message.reply_text(error_message)
            except:
                pass
            print(f"Error processing voice: {e}")
    
    async def handle_audio(update: Update, context):
        """Handle audio files"""
        try:
            audio_file = await update.message.audio.get_file()
            
            file_extension = os.path.splitext(audio_file.file_path)[1] or '.mp3'
            with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_audio:
                temp_path = temp_audio.name
                await audio_file.download_to_drive(temp_path)
            
            # Transcribe audio
            with open(temp_path, 'rb') as audio:
                transcript = openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="es"
                )
            
            os.unlink(temp_path)
            
            # Process with agent
            transcribed_text = transcript.text
            response = agent.process_query(transcribed_text)
            
            # Send single combined response
            combined_response = f"📝 Transcripción: {transcribed_text}\n\n{response}"
            await update.message.reply_text(combined_response)
            
        except Exception as e:
            error_message = f"❌ Error: {str(e)}"
            try:
                await update.message.reply_text(error_message)
            except:
                pass
            print(f"Error processing audio: {e}")
    
    # Register handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    app.add_handler(MessageHandler(filters.AUDIO, handle_audio))


async def process_update(update_data):
    """Process a single Telegram update"""
    try:
        # Initialize components if needed
        initialize_components()
        
        # Initialize the application for this request
        await application.initialize()
        
        # Create Update object from JSON
        update = Update.de_json(update_data, application.bot)
        
        # Process the update
        await application.process_update(update)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'ok'})
        }
    
    except Exception as e:
        print(f"Error processing update: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Receives webhook from Telegram via API Gateway
    """
    
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse the body (API Gateway sends it as string)
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        # Handle Telegram webhook
        if body:
            # Run async function synchronously
            import asyncio
            result = asyncio.run(process_update(body))
            return result
        
        # Health check endpoint
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'Bot is running'})
        }
    
    except Exception as e:
        print(f"Lambda handler error: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

