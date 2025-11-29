#!/usr/bin/env python3
"""
Script para configurar el webhook de Telegram
Uso: python setup_webhook.py <webhook_url>
"""

import sys
import os
import requests
from dotenv import load_dotenv


def set_webhook(bot_token, webhook_url):
    """Configure Telegram webhook"""
    url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
    
    payload = {
        "url": webhook_url,
        "allowed_updates": ["message", "edited_message"]
    }
    
    print(f"🔗 Configurando webhook...")
    print(f"   Bot token: {bot_token[:10]}...")
    print(f"   Webhook URL: {webhook_url}")
    
    response = requests.post(url, json=payload)
    result = response.json()
    
    if result.get("ok"):
        print("✅ Webhook configurado exitosamente!")
        return True
    else:
        print(f"❌ Error: {result.get('description', 'Unknown error')}")
        return False


def get_webhook_info(bot_token):
    """Get current webhook info"""
    url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
    
    response = requests.get(url)
    result = response.json()
    
    if result.get("ok"):
        info = result.get("result", {})
        print("\n📋 Información del webhook:")
        print(f"   URL: {info.get('url', 'No configurado')}")
        print(f"   Pending updates: {info.get('pending_update_count', 0)}")
        print(f"   Max connections: {info.get('max_connections', 0)}")
        if info.get('last_error_message'):
            print(f"   ⚠️  Último error: {info.get('last_error_message')}")
        return info
    else:
        print(f"❌ Error obteniendo info: {result.get('description')}")
        return None


def delete_webhook(bot_token):
    """Delete webhook (switch back to polling)"""
    url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
    
    print("🗑️  Eliminando webhook...")
    response = requests.post(url)
    result = response.json()
    
    if result.get("ok"):
        print("✅ Webhook eliminado. Ahora puedes usar polling.")
        return True
    else:
        print(f"❌ Error: {result.get('description')}")
        return False


def main():
    # Load environment variables
    load_dotenv()
    
    bot_token = os.getenv('TELEGRAM_API')
    
    if not bot_token:
        print("❌ Error: TELEGRAM_API no encontrado en .env")
        sys.exit(1)
    
    print("🤖 Telegram Webhook Setup")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "info":
            # Show webhook info
            get_webhook_info(bot_token)
        
        elif command == "delete":
            # Delete webhook
            delete_webhook(bot_token)
        
        elif command.startswith("http"):
            # Set webhook with provided URL
            webhook_url = sys.argv[1]
            if set_webhook(bot_token, webhook_url):
                print("\n")
                get_webhook_info(bot_token)
        
        else:
            print(f"❌ Comando desconocido: {command}")
            print_usage()
    
    else:
        print_usage()


def print_usage():
    """Print usage information"""
    print("\n📖 Uso:")
    print("   python setup_webhook.py <webhook_url>  - Configurar webhook")
    print("   python setup_webhook.py info            - Ver info del webhook")
    print("   python setup_webhook.py delete          - Eliminar webhook")
    print("\n📝 Ejemplos:")
    print("   python setup_webhook.py https://abc.execute-api.us-east-1.amazonaws.com/prod/webhook")
    print("   python setup_webhook.py info")
    print("   python setup_webhook.py delete")
    print("")


if __name__ == "__main__":
    main()

