"""
Main entry point for the Leads/Contacts Telegram Bot
"""

import os
from dotenv import load_dotenv
from sheets_manager import SheetsManager
from agent import LeadsAgent
from telegram_bot import TelegramBot


def main():
    """Main function to start the bot"""
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment
    telegram_token = os.getenv('TELEGRAM_API')
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    openai_api_key = os.getenv('OPENAI_API_KEY')
    
    # Validate required environment variables
    if not telegram_token:
        raise ValueError("TELEGRAM_API not found in environment variables")
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID not found in environment variables")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    # Path to Google credentials file
    credentials_file = 'asociate-f8e54014d9ea.json'
    
    if not os.path.exists(credentials_file):
        raise FileNotFoundError(f"Credentials file not found: {credentials_file}")
    
    print("🔧 Inicializando componentes...")
    
    # Initialize Google Sheets Manager
    print("📊 Conectando a Google Sheets...")
    sheets_manager = SheetsManager(credentials_file, spreadsheet_id)
    
    # Initialize AI Agent
    print("🤖 Inicializando agente de IA...")
    agent = LeadsAgent(sheets_manager, openai_api_key, credentials_file)
    
    # Initialize Telegram Bot
    print("📱 Inicializando bot de Telegram...")
    bot = TelegramBot(telegram_token, agent, openai_api_key)
    
    # Start the bot
    print("\n✅ Sistema listo!")
    print("=" * 50)
    print("Bot de Leads/Contactos iniciado correctamente")
    print("=" * 50)
    print("\nPresiona Ctrl+C para detener el bot\n")
    
    bot.run()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Bot detenido por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise

