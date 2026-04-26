# Bank Statement Parser

An AI-powered tool that extracts and structures transactions 
from any bank statement PDF — digital or scanned.

## Problem it solves
Accountants in CS firms manually re-type bank transactions 
from PDFs into Excel every month. This tool automates that 
entire process using OCR + Gemini AI.

## Tech Stack
- **Backend:** Python, FastAPI, PyMuPDF, Tesseract OCR
- **AI:** Google Gemini API
- **Frontend:** React, Tailwind CSS
- **Database:** SQLite
- **Deployment:** Docker, Render, Vercel

## Features
- Upload any bank PDF (SBI, HDFC, Axis, etc.)
- Auto-extract all transactions with date, debit, credit, balance
- Detect mismatches and anomalies automatically
- Export clean Excel/CSV file
- Beautiful dashboard UI

## Status
🔨 Currently under development