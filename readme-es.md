# Review Booster 🚀

Review Booster es un SaaS ligero y automatizado, diseñado para ayudar a las empresas a enviar invitaciones de reseña personalizadas a sus clientes a través de WhatsApp. Está optimizado específicamente para gestionar el seguimiento de pagos locales, como SINPE Móvil.

## Características
* **Invitaciones automatizadas por WhatsApp**: Envía solicitudes de reseña personalizadas directamente a tus clientes.

* **Integración con SINPE**: Identifica fácilmente las transacciones pagadas mediante SINPE Móvil para activar un mensaje personalizado para dichos clientes.

* **Registro de transacciones**: Registra automáticamente todas las invitaciones enviadas en una base de datos local SQLite con indicadores visuales de estado.

* **Panel de control responsivo**: Una interfaz diseñada principalmente para dispositivos móviles (mobile-first) para gestionar las invitaciones desde cualquier lugar.

## Prerequisitos
* Python 3.8+
* [Cuenta Twilio](https://www.twilio.com/) (para mensajeo de WhatsApp)

## Instrucciones de configuración

### 1. Instalación
Clona el repositorio e instala las dependencias necesarias:

```bash
pip install fastapi uvicorn twilio python-dotenv
```

### 2. Configuración
Crea un archivo llamado `.env` en el directorio raíz del proyecto. Agrega tus credenciales de API específicas y los detalles de tu negocio:

```env
# Configuración de Twilio
TWILIO_ACCOUNT_SID=tu_twilio_account_sid
TWILIO_AUTH_TOKEN=tu_twilio_auth_token

# Configuración del negocio
BUSINESS_NAME=Nombre de tu negocio
```

Para que Review Booster envíe a tus clientes al lugar correcto, debes configurar tu enlace de `Google Maps`:

**¿Dónde encontrarlo?**: Ve a tu perfil de negocio en Google, haz clic en `"Pedir reseñas"` y copia el enlace generado.

**¿Dónde cambiarlo?**: Por el momento, el enlace se introduce directamente en el `formulario del Panel de control (Dashboard)` cada vez que envías una invitación. Esto te permite enviar diferentes enlaces si tienes múltiples sucursales o diferentes productos.

### 3. Ejecución de la Aplicación
Inicia el servidor backend utilizando Uvicorn:

```bash
uvicorn main:app --reload
```

### 4. Acceso al Panel de Control
Una vez que el servidor esté en ejecución, abre tu navegador y dirígete a `http://127.0.0.1:8000`.

### 5. Uso
* Ingresa el nombre del cliente, su número de teléfono (XXXX-XXXX) y el enlace a su reseña de Google.
* Marca la casilla **"¿Fue pago por SINPE Móvil?"** si el cliente utilizó SINPE para activar la lógica de mensajería específica.
* Haz clic en **"Send WhatsApp Invite"**.
* Consulta tu historial en la tabla de **Recent Invitations Log** (Registro de invitaciones recientes) ubicada debajo del formulario.

### 6. Reseting the Database
Review Booster utiliza SQLite para la persistencia local de datos.
* **Archivo de base de datos**: Todas las invitaciones se registran en un archivo llamado `review_booster.db` que se crea en el directorio raíz.
* **Inicialización**: La base de datos y la tabla `invitations` se inicializan automáticamente la primera vez que ejecutas la aplicación.
* **Respaldo**: Dado que es un archivo local, puedes simplemente realizar una copia de seguridad de `review_booster.db` para guardar tu historial de invitaciones.

### Notas
* Dado que este producto está diseñado para ser operado en Costa Rica, un país de habla hispana, se incluyen versiones en español.
* **Elimina** la versión de idioma que no vayas a utilizar.
* Opción 1: Si deseas utilizar la versión en inglés, conserva los archivos `readme-en.md` e `index.html`. Elimina los archivos: `readme-es.md` e `index-esp.html`
* Opción 2: Si deseas utilizar la versión en español, conserva los archivos `readme-es.md` e `index-esp.html`. Elimina los archivos: `readme-en.md` e `index.html`. NOTA: Una vez que el archivo `index.html` (versión en inglés) haya sido eliminado, renombra `index-esp.html` a `index.html`.