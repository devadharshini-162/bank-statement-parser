# StatementAI: Project Progress Documentation

This document summarizes the current state of the **Bank Statement Parser** project, detailing the features added across frontend, backend, cloud, and deployment.

---

## 🎨 Frontend Features
The frontend is a modern, responsive single-page application (SPA) built with **React** and **Vite**, designed with a premium, dashboard-centric aesthetic.

- **Authentication System**:
  - Secure Login/Signup interfaces.
  - JWT (JSON Web Token) persistence in `localStorage`.
- **Intelligent Statement Parsing**:
  - Drag-and-drop PDF upload zone.
  - Dynamic loading states with descriptive processing steps (e.g., "Extracting content", "Analysing with Gemini AI").
- **Interactive Dashboards**:
  - **Spending Analytics**: Categorized pie charts showing distribution of expenses (Food, Transport, Salary, etc.) using `recharts`.
  - **Stat Overview**: Quick-glance cards for total transactions, debits, credits, and detected anomalies.
- **Transaction Explorer**:
  - Robust table with real-time search/filtering.
  - **Anomaly Highlighting**: Visual indicators (gold icons/row shading) for transactions flagged during validation.
- **History Management**:
  - A persistent history modal allowing users to review and re-download previous parsing results.
- **Premium UI/UX**:
  - Glassmorphism effects, mesh backgrounds, and smooth "fade-up" animations.
  - Fully responsive design using custom CSS variables and flexible layouts.

---

## ⚙️ Backend Works
The backend is a high-performance **FastAPI** service that manages the core logic, AI integration, and user data.

- **AI-Powered Extraction**:
  - Integration with **Google Gemini Pro Vision** to extract structured transaction data from any PDF format.
  - Hybrid parsing logic that handles both digital (text-based) and scanned (image-based) bank statements.
- **Robust Authentication (JWT)**:
  - Password hashing with `passlib` (BCrypt).
  - Secure token-based access control for all sensitive endpoints (`/parse`, `/history`).
- **Data Model & Multi-tenancy**:
  - **Relational DB Setup**: Users are linked to their history via foreign keys in SQLAlchemy.
  - **Role-Based Access**: Admins can see company-wide history, while Accountants only see their own.
- **Financial Validation Engine**:
  - Post-extraction validation to check total debits/credits vs. balance changes.
  - Anomaly detection logic to find missing rows or incorrect mathematical structures.
- **Excel Generation**:
  - Dynamic generation of XLSX files with formatted headers and auto-sized columns using `pandas`.

---

## ☁️ Cloud & Infrastructure
The project is built with a "Cloud-First" philosophy, making it ready for production scaling.

- **Storage (AWS S3)**:
  - Logic to upload processed Excel files directly to Amazon S3.
  - **Presigned URLs**: Secure, time-expiring download links generated directly from AWS for maximum security.
- **Database (AWS RDS Ready)**:
  - Currently using local SQLite for development, but fully abstracted via SQLAlchemy to switch to an AWS RDS PostgreSQL instance via a single environment variable.
- **Containerization**:
  - Full **Dockerfile** provided for the backend, ensuring consistent behavior between development, staging, and production.
- **CI/CD Automation**:
  - GitHub Actions workflow (`python-app.yml`) to automatically test the backend on every push.

---

## 🛠️ Tech Stack
- **Frontend**: React, Vite, Lucide-React, Recharts, Axios.
- **Backend**: FastAPI, SQLAlchemy, Uvicorn, Pydantic.
- **AI**: Google Gemini 1.5 Flash API.
- **Data Processing**: Pandas, OpenPyXL, PDF2Image.
- **Cloud**: Boto3 (AWS SDK), Docker, GitHub Actions.

---
*Last Updated: 2026-05-02*
