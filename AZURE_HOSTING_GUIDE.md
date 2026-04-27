# Hosting on Microsoft Azure: Step-by-Step Guide

This guide details how to deploy the **Psychometric Assessment Platform** (FastAPI + PostgreSQL) to Azure using **Azure App Service** and **Azure Database for PostgreSQL**.

---

## Prerequisites

1.  **Azure Account**: An active Azure subscription.
2.  **Azure CLI**: Installed on your local machine ([Download here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)).
3.  **Git**: For version control and deployment.

---

## Phase 1: Infrastructure Setup

### 1. Login to Azure
Open your terminal and log in:
```bash
az login
```

### 2. Create a Resource Group
Create a container for all your project resources:
```bash
az group create --name psycho-resource-group --location eastus
```

### 3. Create Azure Database for PostgreSQL
Provision a Flexible Server (recommended for better performance/cost control):
```bash
az postgres flexible-server create \
  --resource-group psycho-resource-group \
  --name psycho-db-server \
  --location eastus \
  --admin-user psychoadmin \
  --admin-password YourComplexPassword123! \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --public-access 0.0.0.0
```
> [!IMPORTANT]
> Change the password to something secure. Note down the **Server Name** and **Admin User**.

### 4. Create Azure App Service (Plan & Web App)
Create a Linux-based App Service for your FastAPI app:
```bash
# Create Service Plan
az appservice plan create --name psycho-service-plan --resource-group psycho-resource-group --sku B1 --is-linux

# Create Web App
az webapp create --name psycho-app --resource-group psycho-resource-group --plan psycho-service-plan --runtime "PYTHON:3.11"
```

---

## Phase 2: Configuration

### 1. Database Connection String
Your production `DATABASE_URL` will look like this:
`postgresql://psychoadmin:YourComplexPassword123!@psycho-db-server.postgres.database.azure.com:5432/postgres`

### 2. Set Environment Variables
Configure the App Service with your project's settings:
```bash
az webapp config appsettings set --name psycho-app --resource-group psycho-resource-group --settings \
  DATABASE_URL="postgresql://psychoadmin:YourComplexPassword123!@psycho-db-server.postgres.database.azure.com:5432/postgres" \
  GEMINI_API_KEY="your-gemini-api-key" \
  SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL="True" \
  PORT="8000"
```

---

## Phase 3: Deployment

### Option A: Deployment from Local Git
1.  Configure a deployment user (one-time setup):
    ```bash
    az webapp deployment user set --user-name YourUserName --password YourPassword
    ```
2.  Get the Git URL:
    ```bash
    az webapp deployment source config-local-git --name psycho-app --resource-group psycho-resource-group
    ```
3.  Add the remote and push:
    ```bash
    git remote add azure <PASTE_GIT_URL_FROM_STEP_2>
    git push azure main
    ```

### Option B: CI/CD via GitHub Actions (Recommended)
1.  Go to the **Deployment Center** in the Azure Portal for your Web App.
2.  Select **GitHub** as the source.
3.  Authorize/Select your repository and branch.
4.  Azure will automatically generate a `.github/workflows/main_psycho-app.yml` file and add it to your repo.

---

## Phase 4: Post-Deployment Maintenance

### 1. Database Migrations
Once deployed, you need to run your Alembic migrations on the production database.

**Via Azure SSH:**
1.  Go to the Azure Portal -> Web App -> **SSH**.
2.  Run the following commands:
    ```bash
    python -m alembic upgrade head
    ```

### 2. Seeding Questions
To populate your production database with questions:
```bash
# Inside the Azure SSH console
python seed_questions.py
```

### 3. Google OAuth Redirects
If you are using Google Auth, you must update your **Authorized Redirect URIs** in the [Google Cloud Console](https://console.cloud.google.com/):
- `https://psycho-app.azurewebsites.net/auth/google-verify`
- `https://psycho-app.azurewebsites.net`

---

## Phase 5: Troubleshooting

- **Logs**: View live logs to debug startup issues:
  ```bash
  az webapp log tail --name psycho-app --resource-group psycho-resource-group
  ```
- **Startup Command**: If the app fails to start, go to **Configuration -> General Settings** and set the **Startup Command** to:
  `gunicorn -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 backend.main:app`

---

## Summary of Resources Created
- **Resource Group**: `psycho-resource-group`
- **Postgres Server**: `psycho-db-server`
- **App Service**: `psycho-app`
- **URL**: `https://psycho-app.azurewebsites.net`
