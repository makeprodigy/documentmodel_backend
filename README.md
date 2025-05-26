# Document Management Portal

A full-stack application for managing documents and asking AI-powered questions about them.

## Project Overview

This portal allows users to:
- Register and log in securely
- Upload, view, and delete documents (PDF)
- Ask AI-powered questions about uploaded documents using Google's Gemini API
- Enjoy a modern, responsive UI built with Material-UI

## Tech Stack Used

- **Frontend:** React, Vite, Material-UI
- **Backend:** Django, Django REST Framework
- **AI:** Google Gemini API
- **Authentication:** JWT

## Steps to Run Locally

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the backend directory with:
   ```env
   DJANGO_SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-gemini-api-key-here
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Start the development server:
   ```bash
   python manage.py runserver
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file in the frontend directory with:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```
4. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Register a new account or login with existing credentials
   (
   use these credentials if needed
   username : user
   email: user@email.com
   password: user@1234
   )
2. Upload documents from the dashboard
3. View your uploaded documents
4. Select a document and ask questions about it
5. Get AI-powered answers based on the document content

## Hosting Links

- **Frontend (Live):** [https://documentmodel-frontend.vercel.app/](https://documentmodel-frontend.vercel.app/)
- **Backend (Live):** [https://documentmodel-backend.onrender.com](https://documentmodel-backend.onrender.com)
  - **Note:** If you see a 404 at the root, use [https://documentmodel-backend.onrender.com/api/](https://documentmodel-backend.onrender.com/api/) for API endpoints.
- **Frontend GitHub:** [https://github.com/makeprodigy/documentmodel_frontend.git](https://github.com/makeprodigy/documentmodel_frontend.git)
- **Backend GitHub:** [https://github.com/makeprodigy/documentmodel_backend.git](https://github.com/makeprodigy/documentmodel_backend.git)

## Development

- Backend API runs on: http://localhost:8000
- Frontend development server runs on: http://localhost:5173

## Deployment (for local development)

### Backend Deployment (Render.com)
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy

### Frontend Deployment (Vercel)
1. Connect your GitHub repository to Vercel
2. Set the environment variable `VITE_API_URL` to your backend API URL (e.g., https://documentmodel-backend.onrender.com/api/)
3. Deploy

## License

MIT 