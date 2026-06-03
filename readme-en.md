# Review Booster 🚀

Review Booster is a lightweight, automated SaaS prototype designed to help businesses send customized review invitations to their customers via WhatsApp. It is specifically optimized to handle local payment tracking, such as **SINPE Móvil**.

## Features
* **Automated WhatsApp Invitations**: Send personalized review requests directly to customers.
* **SINPE Integration**: Easily flag transactions paid via SINPE Móvil to trigger a custom message for Sinpe Movil payers.
* **Transaction Logging**: Automatically log all sent invitations to a local SQLite database with visual status indicators.
* **Responsive Dashboard**: A mobile-first interface to manage invitations on the go.

## Prerequisites
* Python 3.8+
* [Twilio Account](https://www.twilio.com/) (for WhatsApp messaging)

## Setup Instructions

### 1. Installation
Clone the repository and install the required dependencies:

```bash
pip install fastapi uvicorn twilio python-dotenv
```

### 2. Configuration
Create a file named `.env` in the root directory of the project. Add your specific API credentials and business details:

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+1XXXXXXXXXX

# Business Configuration
BUSINESS_NAME=Your Business Name
```

### 3. Running the Application
Start the backend server using Uvicorn:

```bash
uvicorn main:app --reload
```

### 4. Accessing the Dashboard
Once the server is running, open your browser and navigate to `http://127.0.0.1:8000`.

### 5. Usage
* Enter the customer's name, phone number (in international format), and their Google Review link.
* Check the **"¿Fue pago por SINPE Móvil?"** box if the customer used SINPE to trigger the specific messaging logic.
* Click **"Send WhatsApp Invite"**.
* View your history in the **Recent Invitations Log** table located below the form.

### 6. Reseting the Database
Review Booster uses **SQLite** for local data persistence.
* **Database File**: All invitations are logged to a file named `review_booster.db` created in the root directory.
* **Initialization**: The database and the `invitations` table are automatically initialized the first time you run the application.
* **Backup**: Since this is a local file, you can simply back up `review_booster.db` to save your invitation history.

### Notes
* Since this product is designed to be operated in Costa Rica, a spanish speaking country, spanish versions are included.
* **Delete** the language version you will not use
* Option 1: If you wish to use english version keep files `readme-en.md` and `index.html`. Delete the files: `readme-es.md` and `index-esp.html` 
* Option 2: If you wish to use the spanish version keep files `readme-es.md` and `index-esp.html`. Delete the files: `readme-en.md` and `index.html`. **NOTE** Once `index.html` (english version) is deleted, rename `index-esp.html` to `index.html`