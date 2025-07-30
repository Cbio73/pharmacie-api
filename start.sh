#!/bin/bash
echo "Création de la base si nécessaire..."
python main.py
echo "Démarrage de l'API..."
uvicorn main:app --host 0.0.0.0 --port 10000