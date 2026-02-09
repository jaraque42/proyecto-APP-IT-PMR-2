# Uso de Docker (Windows)

Pasos rápidos:

1) Copia el ejemplo de variables de entorno y ajusta la clave secreta:

   copy .env.example .env
   (Editar `.env` y cambiar SECRET_KEY)

2) Construir la imagen:

   docker build -t appitpmr .

3) Ejecutar con Docker:

   docker run --rm -p 5000:5000 -v %cd%\pdfs:/app/pdfs -v %cd%\entregas.db:/app/entregas.db appitpmr

   - En PowerShell usa `${PWD}` en lugar de `%cd%`:
     `docker run --rm -p 5000:5000 -v ${PWD}\pdfs:/app/pdfs -v ${PWD}\entregas.db:/app/entregas.db appitpmr`

4) Usando Docker Compose (recomendado para desarrollo/gestion):

   docker compose up --build -d

   y luego abrir: http://localhost:5000

Notas:
- Asegúrate de tener Docker Desktop instalado (Windows Home requiere WSL2).
- El `docker-compose.yml` monta la carpeta del proyecto para desarrollo; quita ese volumen en producción si quieres un contenedor inmutable.
- Establece `SECRET_KEY` en `.env` y no lo incluyas en el repo.
- Si aparece algún problema al instalar dependencias que requieran compilación, instala las herramientas de compilación (ya incluimos `gcc` en la imagen base como ayuda).
