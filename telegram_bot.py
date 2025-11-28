"""
Telegram Bot Handler
Receives messages and audio from Telegram, transcribes audio, and processes with the agent
"""

import os
import tempfile
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from agent import LeadsAgent


class TelegramBot:
    """Handles Telegram bot interactions"""
    
    def __init__(self, telegram_token: str, agent: LeadsAgent, openai_api_key: str):
        """
        Initialize the Telegram bot
        
        Args:
            telegram_token: Telegram bot API token
            agent: Instance of LeadsAgent
            openai_api_key: OpenAI API key for transcription
        """
        self.agent = agent
        self.openai_client = OpenAI(api_key=openai_api_key)
        
        # Create the Application
        self.application = Application.builder().token(telegram_token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
        self.application.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        self.application.add_handler(MessageHandler(filters.AUDIO, self.handle_audio))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = """
¡Hola! 👋

Soy tu asistente de Leads y Contactos. Puedo ayudarte a:

📋 Buscar contactos por nombre, empresa o rol
✏️ Actualizar información de contactos
📝 Añadir notas a la bitácora
🎤 Procesar comandos por voz

Puedes enviarme mensajes de texto o notas de voz. Por ejemplo:
- "Busca a Pablo Salomón"
- "¿Quién trabaja en Tech Corp?"
- "Agrega a la bio de Pablo Salomón que tiene dos hijas llamadas Caia y Mirta"

Usa /help para ver más ejemplos.
        """
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = """
📚 Comandos y ejemplos:

🔍 BÚSQUEDAS:
• "Busca a [nombre]"
• "¿Quién es [nombre]?"
• "Muestra los contactos de [empresa]"
• "Lista personas con rol de [rol]"
• "Muestra todos los contactos"

✏️ ACTUALIZACIONES:
• "Agrega a la bio de [nombre] que [información]"
• "Actualiza el teléfono de [nombre] a [número]"
• "Cambia la empresa de [nombre] a [empresa]"
• "Actualiza el rol de [nombre] a [rol]"

📝 BITÁCORA:
• "Añade a la bitácora de [nombre]: [nota]"
• "Registra que [nombre] [acción/nota]"

🎤 Puedes usar notas de voz para cualquier comando!
        """
        await update.message.reply_text(help_message)
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_message = update.message.text
        user_name = update.effective_user.first_name
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        # Process with agent
        response = self.agent.process_query(user_message)
        
        # Send response
        await update.message.reply_text(response)
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        try:
            # Show typing indicator
            await update.message.chat.send_action("typing")
            
            # Download voice file
            voice_file = await update.message.voice.get_file()
            
            # Create a temporary file to store the voice message
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_audio:
                temp_path = temp_audio.name
                await voice_file.download_to_drive(temp_path)
            
            # Transcribe audio using OpenAI Whisper
            await update.message.reply_text("🎤 Transcribiendo audio...")
            
            with open(temp_path, 'rb') as audio_file:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"  # Spanish
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Get transcribed text
            transcribed_text = transcript.text
            
            # Send transcribed text to user
            await update.message.reply_text(f"📝 Transcripción: {transcribed_text}")
            
            # Process with agent
            await update.message.chat.send_action("typing")
            response = self.agent.process_query(transcribed_text)
            
            # Send response
            await update.message.reply_text(response)
            
        except Exception as e:
            error_message = f"❌ Error al procesar el audio: {str(e)}"
            await update.message.reply_text(error_message)
            print(f"Error processing voice: {e}")
    
    async def handle_audio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle audio files"""
        try:
            # Show typing indicator
            await update.message.chat.send_action("typing")
            
            # Download audio file
            audio_file = await update.message.audio.get_file()
            
            # Create a temporary file
            file_extension = os.path.splitext(audio_file.file_path)[1] or '.mp3'
            with tempfile.NamedTemporaryFile(suffix=file_extension, delete=False) as temp_audio:
                temp_path = temp_audio.name
                await audio_file.download_to_drive(temp_path)
            
            # Transcribe audio
            await update.message.reply_text("🎤 Transcribiendo audio...")
            
            with open(temp_path, 'rb') as audio:
                transcript = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="es"
                )
            
            # Clean up temp file
            os.unlink(temp_path)
            
            # Get transcribed text
            transcribed_text = transcript.text
            
            # Send transcribed text
            await update.message.reply_text(f"📝 Transcripción: {transcribed_text}")
            
            # Process with agent
            await update.message.chat.send_action("typing")
            response = self.agent.process_query(transcribed_text)
            
            # Send response
            await update.message.reply_text(response)
            
        except Exception as e:
            error_message = f"❌ Error al procesar el audio: {str(e)}"
            await update.message.reply_text(error_message)
            print(f"Error processing audio: {e}")
    
    def run(self):
        """Start the bot"""
        print("🤖 Bot iniciado y esperando mensajes...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

