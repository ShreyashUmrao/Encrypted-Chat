**EncryptedChat**

A modern real-time encrypted chat application built with FastAPI, React, WebSockets, and AES-256 end-to-end encryption.
Includes multi-room support, JWT authentication, and a custom toxicity detection ML model (retrainable).<br><br><br><br>

Demo

Live Demo: http://152.67.164.57:3000<br><br><br><br>


Features

Security:  
AES-256 (CBC) encryption for every message  
Per-room symmetric keys  
JWT-based user authentication  
Optional user-level toxicity filtering (hide toxic messages)  

Chat Features:  
Multi-room chat system  
Real-time messaging using WebSockets  
Message history saved in PostgreSQL  
Decrypt messages locally on client side   

Machine Learning:  
SBERT-based toxicity classifier  
Supports custom datasets (text, label)  

Docker Ready:  
Full production-ready Docker setup  
Backend (FastAPI)  
Frontend (React + Nginx)  
PostgreSQL  
Single command startup<br><br><br><br>  


Tech Stack  

Frontend:  
React + Vite  
Tailwind CSS  
WebSockets API  
CryptoJS AES-CBC Encryption  

Backend:  
FastAPI  
SQLAlchemy  
Uvicorn     
PyCryptodome (AES-256 encryption)  
python-jose (JWT)  

Machine Learning:   
SentenceTransformers (SBERT)  
scikit-learn  
joblib  
pandas  

Database:  
PostgreSQL   
SQLAlchemy ORM  

DevOps:  
Docker & Docker Compose  
Nginx (for frontend)<br><br><br><br>  


Running With Docker  

Add .env file for backend  

Run inside project root:  
docker compose up --build  

This starts:  
Backend	http://localhost:8000  
Frontend	http://localhost:3000  
PostgreSQL	localhost:5432<br><br><br><br>  


Toxicity Model — How to Rebuild & Use  

The project expects the SBERT model + classifier to be stored inside:  

backend/app/models/  
    ├── sbert_encoder/       
    ├── sbert_model.pkl       
    ├── sbert_threshold.txt    

Retrain using CSV

Your CSV must contain:  
text - 	           label  
Toxic Text -            1  
Non-Toxic Text -   	    0  

Train model and save model files into /app/models/
