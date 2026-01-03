# 🧠 Migraine Tracking Feature

## Overview
Added a new tool to the agent that allows registering migraine episodes to a separate Google Sheet.

## Google Sheet Details
- **Sheet ID**: `1Kp9c47qgiQQgDTdRq9vwkWIZsX7zfeVSTEtVJuy8qmA`
- **URL**: https://docs.google.com/spreadsheets/d/1Kp9c47qgiQQgDTdRq9vwkWIZsX7zfeVSTEtVJuy8qmA/edit?gid=0#gid=0
- **Permissions**: Already shared with the service account

## Sheet Structure
The migraine sheet has 3 columns:

| Fecha | Intensidad | Posible causa |
|-------|------------|---------------|
| DD/MM/YYYY | Baja/Media/Alta | Text description |

## How to Use

### Via Telegram Bot
Simply send a message mentioning migraine registration. Examples:

```
"Registra una migraña de hoy, intensidad alta, posible causa: estrés laboral"

"Tengo una migraña media, creo que fue por falta de sueño"

"Registra dolor de cabeza intensidad baja, causa: cambio de clima"
```

### What the Agent Does
1. **Detects migraine registration requests** using keywords: migraña, dolor de cabeza, jaqueca, cefalea
2. **Gets current date** if user mentions "hoy" or "today" (using `get_current_datetime` tool)
3. **Extracts information** from the message:
   - Intensity (baja/media/alta or numerical)
   - Possible cause
4. **Registers** the episode in the migraine sheet
5. **Confirms** to the user with a summary

## Code Changes

### 1. `agent.py`
- **Updated `__init__`**: Added `credentials_file` parameter and initialized `migraine_manager`
- **Added `register_migraine_tool`**: New tool function to handle migraine registration
- **Updated system prompt**: Added instructions for migraine tracking
- **Added tool to tools list**: Registered the new tool

### 2. `main.py`
- **Updated agent initialization**: Now passes `credentials_file` to `LeadsAgent`

### 3. `lambda_function.py`
- **Updated agent initialization**: Now passes `credentials_file` to `LeadsAgent`

### 4. `sheets_manager.py`
- **Made `add_record` method flexible**: Now dynamically reads headers from the sheet instead of hardcoding column order
- This allows the same `SheetsManager` class to work with different sheet structures

## Technical Details

### Tool Definition
```python
def register_migraine_tool(input_str: str) -> str:
    """
    Register a migraine episode to the migraine tracking sheet.
    Input format: 'fecha|intensidad|posible_causa'
    """
```

### System Prompt Addition
```
IMPORTANTE - Registro de migrañas:
- Cuando el usuario mencione palabras como "migraña", "dolor de cabeza", "jaqueca", "cefalea" y pida registrar, usa la herramienta register_migraine
- SIEMPRE usa get_current_datetime primero si el usuario menciona "hoy", "today" o no especifica fecha
- Extrae del mensaje del usuario: la intensidad (baja/media/alta o numérica) y la posible causa
- Si falta alguna información, pregunta al usuario por ella antes de registrar
- Confirma al usuario que el episodio fue registrado exitosamente
```

## Example Flow

**User**: "Registra una migraña de hoy, intensidad alta, por estrés"

**Agent Actions**:
1. Calls `get_current_datetime()` → Gets "03/01/2026"
2. Calls `register_migraine("03/01/2026|Alta|Estrés")`
3. Responds: "✅ Migraña registrada exitosamente:
   - Fecha: 03/01/2026
   - Intensidad: Alta
   - Posible causa: Estrés"

## Testing

To test the feature:

1. **Local testing**:
```bash
python main.py
```
Then send a message via Telegram: "Registra una migraña de hoy, intensidad media, causa: falta de sueño"

2. **Lambda testing**:
After deployment, send the same message to your bot.

## Notes

- The same Google service account credentials are used for both sheets
- The migraine sheet must have the exact column names: `Fecha`, `Intensidad`, `Posible causa`
- The agent automatically uses today's date if the user says "hoy" or "today"
- The feature is fully integrated with the existing agent system
