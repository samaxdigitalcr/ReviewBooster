# Review Booster 🚀

Review Booster es una aplicación diseñada para automatizar el envío de solicitudes de reseñas de Google a través de WhatsApp, facilitando la gestión de la reputación de negocios locales.

## 🛠️ Tecnologías Utilizadas
- **Backend:** FastAPI (Python)
- **Base de Datos:** PostgreSQL (vía Neon)
- **ORM:** SQLAlchemy
- **Automatización:** Twilio API para WhatsApp
- **Frontend:** HTML con Jinja2 Templates
- **Despliegue:** Render

## ⚙️ Características Técnicas
- **Gestión robusta de conexiones:** Implementación de `pool_pre_ping` y `pool_recycle` con SQLAlchemy para evitar desconexiones (SSL EOF errors) en entornos serverless.
- **Seguridad:** Manejo de variables de entorno para credenciales sensibles.
- **Normalización de datos:** Limpieza automática de números telefónicos de Costa Rica.
- **Historial:** Registro y visualización de invitaciones enviadas.

## 🚀 Despliegue en Render
Para que la aplicación funcione correctamente en Render:
1. **Variables de Entorno:** Debes configurar:
   - `DATABASE_URL`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_NUMBER`
   - `BUSINESS_NAME`

2. **Comando de Inicio:**
   Se recomienda usar el siguiente comando para optimizar el uso de conexiones a la BD:
   `gunicorn -w 2 -k uvicorn.workers.UvicornWorker main:app`

## 📝 Cómo contribuir
1. Haz un fork del proyecto.
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`).
4. Haz push a la rama (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

---
*Desarrollado con ❤️ por Samax Digital CR*
