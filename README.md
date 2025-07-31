# Convertidor de MP3 a MPEG

Este es un microservicio simple construido con Python y Flask que convierte archivos de audio de formato MP3 a MPEG. El servicio está dockerizado y listo para ser desplegado en plataformas como Railway.

## Características

- Endpoint de API para convertir archivos MP3 a MPEG.
- Manejo de archivos temporales de forma segura.
- Contenedorizado con Docker para un despliegue sencillo.

## Endpoint de la API

### POST /convert

Convierte un archivo MP3 a MPEG.

**Request:**

- **Método:** `POST`
- **URL:** `/convert`
- **Body:** `multipart/form-data`
  - **key:** `file`
  - **value:** El archivo MP3 que deseas convertir.

**Respuesta Exitosa:**

- **Código de Estado:** `200 OK`
- **Content-Type:** `audio/mpeg`
- **Body:** El archivo de audio convertido en formato MPEG.

**Respuesta de Error:**

- **Código de Estado:** `400 Bad Request` o `500 Internal Server Error`
- **Content-Type:** `application/json`
- **Body:** Un objeto JSON con un mensaje de error.
  ```json
  { "error": "Mensaje de error detallado" }
  ```

## Cómo usarlo localmente

Para ejecutar este servicio en tu máquina local, necesitarás tener Docker instalado.

1.  **Clona el repositorio:**

    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd mp3-to-mpeg-converter
    ```

2.  **Construye la imagen de Docker:**

    ```bash
    docker build -t mp3-to-mpeg-converter .
    ```

3.  **Ejecuta el contenedor:**
    ```bash
    docker run -p 8080:8080 mp3-to-mpeg-converter
    ```

El servicio estará disponible en `http://localhost:8080`.

## Despliegue en Railway

1.  Sube este repositorio a tu cuenta de GitHub.
2.  Crea un nuevo proyecto en Railway.
3.  Selecciona "Deploy from GitHub repo" y elige tu repositorio.
4.  Railway detectará automáticamente el `Dockerfile` y desplegará el servicio. No se necesita configuración adicional.
