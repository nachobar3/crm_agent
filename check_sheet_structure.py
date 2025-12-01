"""
Script para verificar la estructura de tu Google Sheet
Muestra los encabezados actuales y un registro de ejemplo
"""

import os
from dotenv import load_dotenv
from sheets_manager import SheetsManager

def main():
    # Load environment variables
    load_dotenv()
    
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    credentials_file = 'asociate-f8e54014d9ea.json'
    
    if not spreadsheet_id:
        print("❌ Error: SPREADSHEET_ID no encontrado en .env")
        return
    
    if not os.path.exists(credentials_file):
        print(f"❌ Error: Archivo de credenciales no encontrado: {credentials_file}")
        return
    
    print("🔍 Verificando estructura de Google Sheet...\n")
    
    # Initialize Google Sheets Manager
    sheets_manager = SheetsManager(credentials_file, spreadsheet_id)
    
    # Get the sheet
    sheet = sheets_manager.sheet
    
    # Get headers (first row)
    headers = sheet.row_values(1)
    
    print("📋 ENCABEZADOS DE LA HOJA:")
    print("=" * 60)
    for i, header in enumerate(headers, 1):
        print(f"  Columna {i}: '{header}'")
    
    print("\n" + "=" * 60)
    print("\n✅ ENCABEZADOS ESPERADOS (nueva estructura):")
    expected = ['Nombre', 'Teléfono', 'Email', 'Telegram', 'Empresa', 'Rol', 'bio', 'bitácora']
    for i, exp_header in enumerate(expected, 1):
        print(f"  Columna {i}: '{exp_header}'")
    
    # Check if headers match
    print("\n" + "=" * 60)
    print("\n🔎 COMPARACIÓN:")
    all_match = True
    for i, exp_header in enumerate(expected):
        if i < len(headers):
            actual = headers[i]
            match = "✅" if actual == exp_header else "❌"
            print(f"  {match} Columna {i+1}: Esperado '{exp_header}' | Actual '{actual}'")
            if actual != exp_header:
                all_match = False
        else:
            print(f"  ❌ Columna {i+1}: Esperado '{exp_header}' | FALTANTE")
            all_match = False
    
    # Get sample data
    print("\n" + "=" * 60)
    print("\n📊 REGISTRO DE EJEMPLO (primera fila de datos):")
    all_records = sheets_manager.get_all_records()
    if all_records:
        first_record = all_records[0]
        print("\nClaves disponibles en el registro:")
        for key, value in first_record.items():
            value_display = value if value else "(vacío)"
            print(f"  • {key}: {value_display}")
    else:
        print("  ⚠️ No hay registros en la hoja")
    
    print("\n" + "=" * 60)
    
    if all_match:
        print("\n✅ La estructura de tu hoja es CORRECTA")
    else:
        print("\n❌ La estructura de tu hoja NO coincide con la esperada")
        print("\n📝 ACCIÓN REQUERIDA:")
        print("   1. Abre tu Google Sheet")
        print("   2. Modifica la primera fila (encabezados) para que tenga:")
        print("      Nombre | Teléfono | Email | Telegram | Empresa | Rol | bio | bitácora")
        print("   3. Guarda los cambios")
        print("   4. Vuelve a ejecutar este script para verificar")

if __name__ == "__main__":
    main()

