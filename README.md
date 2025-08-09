# Generador de Videos con IA

Este es un microservicio completo construido con Python y Flask que automatiza todo el proceso de generación de videos desde un script de texto hasta un video final con avatar. Integra ElevenLabs para síntesis de voz, conversión de audio, y HeyGen para generación de videos con avatar.

## Características

- **Síntesis de voz**: Convierte texto a audio usando ElevenLabs con voz en español
- **Conversión de audio**: Convierte MP3 a MPEG internamente
- **Generación de video**: Crea videos con avatar usando HeyGen
- **Notificaciones**: Envía notificaciones opcionales a Microsoft Teams
- **Manejo de estado**: Monitorea el progreso de generación del video
- **Contenedorizado**: Listo para desplegar en Docker y Railway

## Endpoints de la API

### POST /generate-video

Genera un video completo desde un script de texto.

**Request:**

```json
{
  "Script": "Texto que será convertido a voz y usado para generar el video",
  "Titulo": "Título del video (opcional)",
  "Referencias": "Referencias o fuentes (opcional)"
}
```

**Respuesta Exitosa:**

```json
{
  "success": true,
  "message": "Video generated successfully",
  "data": {
    "video_id": "heygen_video_id",
    "video_url": "https://resource.heygen.com/video/...",
    "audio_asset_id": "heygen_audio_asset_id",
    "title": "Título del video",
    "references": "Referencias proporcionadas"
  }
}
```

**Respuesta de Error:**

```json
{
  "success": false,
  "error": "Mensaje de error detallado"
}
```

### GET /health

Endpoint de verificación de salud del servicio.

### GET /

Información general del servicio y endpoints disponibles.

## Configuración

### Variables de Entorno

Copia el archivo `env.example` a `.env` y configura las siguientes variables:

```bash
# ElevenLabs API Configuration
ELEVENLABS_API_KEY=tu_clave_api_elevenlabs
ELEVENLABS_VOICE_ID=4hF8FODW3hjMTvUWqCxk

# HeyGen API Configuration
HEYGEN_API_KEY=tu_clave_api_heygen
HEYGEN_AVATAR_ID=2e4fd9de3aaa4f92bcda52fbe2161431

# Microsoft Teams Configuration (opcional)
TEAMS_WEBHOOK_URL=tu_webhook_url_teams

# Server Configuration
PORT=8080
```

### Obtener las claves API

1. **ElevenLabs**:

   - Regístrate en [elevenlabs.io](https://elevenlabs.io)
   - Ve a tu perfil → API Keys
   - Crea una nueva clave API

2. **HeyGen**:
   - Regístrate en [heygen.com](https://heygen.com)
   - Ve a Settings → API Keys
   - Crea una nueva clave API

## Cómo usarlo localmente

### Con Docker (Recomendado)

1. **Clona el repositorio:**

   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd mp3-to-mpeg-converter
   ```

2. **Configura las variables de entorno:**

   ```bash
   cp env.example .env
   # Edita .env con tus claves API
   ```

3. **Construye y ejecuta:**
   ```bash
   docker build -t video-generator .
   docker run -p 8080:8080 --env-file .env video-generator
   ```

### Sin Docker

1. **Instala las dependencias:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configura las variables de entorno:**

   ```bash
   cp env.example .env
   # Edita .env con tus claves API
   ```

3. **Ejecuta la aplicación:**
   ```bash
   python app.py
   ```

## Ejemplo de uso

```bash
curl -X POST http://localhost:8080/generate-video \
  -H "Content-Type: application/json" \
  -d '{
    "Script": "Hola, este es un ejemplo de script que será convertido a video con avatar",
    "Titulo": "Video de Prueba",
    "Referencias": "Fuente: Ejemplo de prueba"
  }'
```

## Despliegue en Railway

1. Sube este repositorio a tu cuenta de GitHub
2. Crea un nuevo proyecto en Railway
3. Selecciona "Deploy from GitHub repo" y elige tu repositorio
4. Configura las variables de entorno en Railway:
   - Ve a Variables → Environment Variables
   - Añade todas las variables del archivo `env.example`
5. Railway desplegará automáticamente el servicio

## Proceso Completo

El servicio ejecuta los siguientes pasos automáticamente:

1. **Recibe el script** a través del endpoint `/generate-video`
2. **Genera audio** usando ElevenLabs TTS con voz en español
3. **Convierte MP3 a MPEG** internamente para compatibilidad
4. **Sube el audio** como asset a HeyGen
5. **Crea el video** usando el avatar configurado
6. **Monitorea el estado** hasta que el video esté listo
7. **Envía notificación** opcional a Teams
8. **Retorna la URL** del video generado

## Notas Importantes

- El proceso puede tomar varios minutos dependiendo de la longitud del script
- Asegúrate de tener créditos suficientes en ElevenLabs y HeyGen
- El servicio incluye timeouts y reintentos para mayor robustez
- Los archivos temporales se limpian automáticamente
