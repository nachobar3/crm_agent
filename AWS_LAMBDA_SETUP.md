# ☁️ Despliegue en AWS Lambda con Webhooks

Esta guía explica cómo desplegar el bot de Telegram en AWS Lambda usando webhooks en lugar de polling.

## 📋 Requisitos Previos

- Cuenta de AWS con permisos de Lambda y API Gateway
- AWS CLI configurado
- Bot de Telegram creado (token de @BotFather)
- Credenciales configuradas (ver `CREDENTIALS_SETUP.md`)

## 🏗️ Arquitectura

```
Telegram → API Gateway → Lambda Function → Google Sheets
                              ↓
                          OpenAI API
```

## 🚀 Paso 1: Crear la Función Lambda

### 1.1 Crear función en AWS Console

1. Ve a AWS Lambda Console
2. Clic en "Create function"
3. Configuración:
   - **Name**: `telegram-leads-bot`
   - **Runtime**: Python 3.11
   - **Architecture**: x86_64
   - **Execution role**: Crear nuevo rol con permisos básicos

### 1.2 Configurar la función

**Configuración básica:**
- **Memory**: 512 MB (mínimo para OpenAI + LangChain)
- **Timeout**: 60 segundos (para transcripciones de audio largas)
- **Ephemeral storage**: 512 MB (default está bien)

**Variables de entorno:**

Agrega estas variables en Configuration → Environment variables:

```
TELEGRAM_API=tu_telegram_bot_token
SPREADSHEET_ID=tu_spreadsheet_id
OPENAI_API_KEY=tu_openai_api_key
GOOGLE_CREDENTIALS_FILE=/tmp/credentials.json
```

### 1.3 Subir credenciales de Google Cloud

Las credenciales de Google deben estar en Lambda. Hay dos opciones:

**Opción A: AWS Secrets Manager (Recomendado para producción)**

1. Sube el JSON a Secrets Manager:
```bash
aws secretsmanager create-secret \
  --name telegram-bot/google-credentials \
  --secret-string file://credentials.json \
  --region us-east-1
```

2. Modifica `lambda_function.py` para leer desde Secrets Manager (código incluido abajo)

3. Agrega permisos al rol de Lambda para leer secrets

**Opción B: Lambda Layer (Más simple para desarrollo)**

1. Crea un layer con las credenciales:
```bash
mkdir python
cp credentials.json python/
zip -r credentials-layer.zip python
```

2. Sube el layer en Lambda Console:
   - Layers → Create layer
   - Name: `google-credentials`
   - Upload: `credentials-layer.zip`
   - Runtime: Python 3.11

3. Adjunta el layer a tu función Lambda

**Opción C: Incluir en deployment package (NO recomendado para producción)**

Incluye el archivo en el ZIP de deployment (menos seguro pero más simple).

## 🌐 Paso 2: Configurar API Gateway

### 2.1 Crear API Gateway

1. Ve a API Gateway Console
2. Clic en "Create API"
3. Selecciona **REST API** (no Private)
4. Configuración:
   - **API name**: `telegram-bot-webhook`
   - **Endpoint Type**: Regional

### 2.2 Crear recurso y método

1. **Crear recurso:**
   - Actions → Create Resource
   - **Resource Name**: `webhook`
   - **Resource Path**: `/webhook`

2. **Crear método POST:**
   - Selecciona el recurso `/webhook`
   - Actions → Create Method → POST
   - **Integration type**: Lambda Function
   - **Lambda Function**: `telegram-leads-bot`
   - Guarda y acepta los permisos

3. **Habilitar CORS (opcional pero recomendado):**
   - Actions → Enable CORS
   - Usar defaults y confirmar

### 2.3 Deploy API

1. Actions → Deploy API
2. **Deployment stage**: `prod` (crear nuevo stage)
3. Anota la **Invoke URL**, ejemplo:
   ```
   https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
   ```

Tu endpoint webhook será:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/webhook
```

## 🔗 Paso 3: Configurar Webhook de Telegram

### 3.1 Setear el webhook

Ejecuta este comando (reemplaza los valores):

```bash
curl -X POST "https://api.telegram.org/bot<TU_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/webhook"
  }'
```

O usando Python:

```python
import requests

BOT_TOKEN = "tu_bot_token"
WEBHOOK_URL = "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/webhook"

response = requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
    json={"url": WEBHOOK_URL}
)

print(response.json())
```

### 3.2 Verificar webhook

```bash
curl "https://api.telegram.org/bot<TU_BOT_TOKEN>/getWebhookInfo"
```

Deberías ver:
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/webhook",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "max_connections": 40
  }
}
```

## 🤖 Paso 4: Configurar GitHub Actions (CI/CD)

### 4.1 Configurar OIDC en AWS

1. Ve a IAM → Identity providers
2. Clic en "Add provider"
3. **Provider type**: OpenID Connect
4. **Provider URL**: `https://token.actions.githubusercontent.com`
5. **Audience**: `sts.amazonaws.com`

### 4.2 Crear rol IAM para GitHub Actions

1. IAM → Roles → Create role
2. **Trusted entity type**: Web identity
3. **Identity provider**: token.actions.githubusercontent.com
4. **Audience**: sts.amazonaws.com
5. **GitHub organization**: tu-usuario
6. **GitHub repository**: crm_agent
7. **GitHub branch**: main

**Permisos necesarios:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:UpdateFunctionCode",
        "lambda:GetFunction"
      ],
      "Resource": "arn:aws:lambda:REGION:ACCOUNT_ID:function:telegram-leads-bot"
    }
  ]
}
```

8. **Role name**: `github-actions-lambda-deploy`
9. Anota el **Role ARN**

### 4.3 Configurar Secrets en GitHub

1. Ve a tu repositorio → Settings → Secrets and variables → Actions
2. Agrega estos secrets:

```
AWS_ROLE_ARN=arn:aws:iam::ACCOUNT_ID:role/github-actions-lambda-deploy
AWS_REGION=us-east-1
LAMBDA_FUNCTION_NAME=telegram-leads-bot
```

### 4.4 Variables de entorno en Lambda

Asegúrate de configurar estas en Lambda Console:

```
TELEGRAM_API=<tu_token>
SPREADSHEET_ID=<tu_id>
OPENAI_API_KEY=<tu_key>
GOOGLE_CREDENTIALS_FILE=/tmp/credentials.json
```

## ✅ Paso 5: Probar el Deployment

### 5.1 Push a GitHub

```bash
git add .
git commit -m "Add Lambda webhook support"
git push
```

GitHub Actions se ejecutará automáticamente y desplegará a Lambda.

### 5.2 Probar el bot

1. Abre Telegram
2. Busca tu bot
3. Envía: `/start`
4. Prueba comandos:
   - "Busca a [nombre]"
   - Envía un audio

### 5.3 Ver logs

Para ver logs en tiempo real:

```bash
aws logs tail /aws/lambda/telegram-leads-bot --follow
```

O en AWS Console:
- CloudWatch → Log groups → `/aws/lambda/telegram-leads-bot`

## 🐛 Troubleshooting

### Error: "Task timed out after 3.00 seconds"
- Aumenta el timeout de Lambda a 60 segundos

### Error: "Unable to import module 'lambda_function'"
- Verifica que todas las dependencias estén en el ZIP
- Chequea que los archivos estén en el root del ZIP, no en subdirectorio

### Error: "No module named 'gspread'"
- Las dependencias no se instalaron correctamente
- Verifica que `requirements.txt` esté en el repo
- Chequea los logs de GitHub Actions

### Webhook no recibe updates
- Verifica que el webhook esté configurado: `getWebhookInfo`
- Chequea que API Gateway tenga el método POST
- Verifica los logs de CloudWatch

### Error: "Service account not found"
- Las credenciales de Google no están disponibles
- Usa AWS Secrets Manager o Lambda Layer
- Verifica la variable `GOOGLE_CREDENTIALS_FILE`

## 💰 Costos Estimados

**AWS Lambda:**
- 1M requests/mes = ~$0.20
- Compute time (512MB, 5s promedio) = ~$4.17/mes para 100k requests

**API Gateway:**
- 1M requests/mes = ~$3.50

**OpenAI:**
- Whisper: $0.006/minuto de audio
- GPT-4o: $2.50/1M tokens input, $10/1M tokens output

**Google Sheets API:**
- Gratis hasta 60 requests/minuto

**Total estimado para uso moderado:** ~$10-20/mes

## 🔒 Mejores Prácticas de Seguridad

1. **Usa AWS Secrets Manager** para credenciales sensibles
2. **Habilita CloudWatch Logs Insights** para monitoreo
3. **Configura alertas** para errores y timeouts
4. **Usa API Gateway con API Keys** (opcional)
5. **Implementa rate limiting** en API Gateway
6. **Rota credenciales** regularmente
7. **Usa VPC** si necesitas recursos privados
8. **Habilita AWS WAF** para protección adicional

## 📚 Recursos Adicionales

- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)
- [API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [Telegram Bot API - Webhooks](https://core.telegram.org/bots/api#setwebhook)
- [GitHub Actions - AWS](https://github.com/aws-actions)

## 🔄 Rollback

Si algo sale mal, puedes hacer rollback:

```bash
# Ver versiones anteriores
aws lambda list-versions-by-function --function-name telegram-leads-bot

# Hacer rollback a versión anterior
aws lambda update-function-configuration \
  --function-name telegram-leads-bot \
  --version $PREVIOUS_VERSION
```

## 🎉 ¡Listo!

Tu bot ahora está desplegado en AWS Lambda con:
- ✅ Webhooks en lugar de polling
- ✅ Escalado automático
- ✅ Deploy continuo con GitHub Actions
- ✅ Arquitectura serverless
- ✅ Costos optimizados

