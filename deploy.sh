#!/bin/bash

# Script de déploiement pour le système de paie Guinée
set -e

echo "🚀 Déploiement du système de paie Guinée"
echo "========================================"

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez installer Docker."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose n'est pas installé. Veuillez installer Docker Compose."
    exit 1
fi

echo "✅ Docker et Docker Compose sont installés"

# Vérification du fichier .env
if [ ! -f .env ]; then
    echo "⚠️  Fichier .env non trouvé. Création à partir de env.example..."
    cp env.example .env
    echo "📝 Veuillez éditer le fichier .env avec vos configurations"
    echo "   nano .env"
    read -p "Appuyez sur Entrée une fois le fichier .env configuré..."
fi

# Arrêt des conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose down

# Construction des images
echo "🔨 Construction des images Docker..."
docker-compose build --no-cache

# Démarrage des services
echo "🚀 Démarrage des services..."
docker-compose up -d

# Attente que les services soient prêts
echo "⏳ Attente que les services soient prêts..."
sleep 10

# Vérification de l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose ps

# Création du superutilisateur
echo "👤 Création du superutilisateur..."
echo "Voulez-vous créer un superutilisateur maintenant ? (y/n)"
read -p "> " create_superuser

if [ "$create_superuser" = "y" ] || [ "$create_superuser" = "Y" ]; then
    docker-compose exec web python manage.py createsuperuser --settings=payroll_project.settings_production
fi

# Affichage des informations de déploiement
echo ""
echo "🎉 Déploiement terminé avec succès!"
echo "=================================="
echo "📊 Application: http://localhost:8000"
echo "🔧 Administration: http://localhost:8000/admin/"
echo "📋 Logs: docker-compose logs -f"
echo "🛑 Arrêt: docker-compose down"
echo ""

# Affichage des logs
echo "📋 Affichage des logs (Ctrl+C pour arrêter)..."
docker-compose logs -f
