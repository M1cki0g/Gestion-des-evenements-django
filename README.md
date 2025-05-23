# Toul Events - Django Event Management System

A Django-based event management system.

## Deployment to Railway

### Prerequisites
- A Railway.app account
- Git installed on your local machine
- Railway CLI (optional)

### Steps to Deploy

1. **Login to Railway**
   - Go to [Railway.app](https://railway.app) and log in
   - Create a new project

2. **Set up your Database**
   - In your Railway project, add a PostgreSQL database
   - Railway will automatically add the DATABASE_URL to your environment variables

3. **Deploy your Application**
   - Use one of these methods:
     - Connect your GitHub repository
     - Deploy directly from CLI: `railway up`
     - Deploy via Railway dashboard

4. **Set Environment Variables**
   In your Railway project settings, add these environment variables:
   - `SECRET_KEY`: Your Django secret key
   - `DEBUG`: Set to "False" for production
   - `EMAIL_HOST_PASSWORD`: Your email password for SMTP
   - Any other required environment variables

5. **Run Database Migrations**
   - In Railway's dashboard, you can run commands like:
     ```
     python manage.py migrate
     python manage.py collectstatic --no-input
     ```

6. **Access your Deployed Application**
   - Railway will provide a URL for your deployed app
   - You can also set up a custom domain in the Railway settings

## Local Development Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your .env file with required variables
4. Run migrations: `python manage.py migrate`
5. Start server: `python manage.py runserver`
