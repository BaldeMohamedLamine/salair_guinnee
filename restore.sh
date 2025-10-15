#!/bin/bash

# Script de restauration pour le système de paie Guinée
set -e

echo "🔄 Restauration du système de paie Guinée"
echo "========================================"

# Configuration
BACKUP_DIR="./backups"

# Vérification du répertoire de sauvegarde
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Répertoire de sauvegarde non trouvé: $BACKUP_DIR"
    exit 1
fi

# Liste des sauvegardes disponibles
echo "📋 Sauvegardes disponibles:"
ls -la $BACKUP_DIR/payroll_backup_*_complete.tar.gz 2>/dev/null || {
    echo "❌ Aucune sauvegarde trouvée"
    exit 1
}

echo ""
echo "Veuillez sélectionner une sauvegarde à restaurer:"
select backup_file in $BACKUP_DIR/payroll_backup_*_complete.tar.gz; do
    if [ -n "$backup_file" ]; then
        break
    else
        echo "❌ Sélection invalide"
    fi
done

echo "🔄 Restauration de: $backup_file"

# Confirmation
echo "⚠️  ATTENTION: Cette opération va remplacer toutes les données actuelles!"
read -p "Êtes-vous sûr de vouloir continuer? (oui/non): " confirm

if [ "$confirm" != "oui" ]; then
    echo "❌ Restauration annulée"
    exit 1
fi

# Arrêt des services
echo "🛑 Arrêt des services..."
docker-compose down

# Extraction de la sauvegarde
echo "📦 Extraction de la sauvegarde..."
TEMP_DIR=$(mktemp -d)
tar -xzf "$backup_file" -C "$TEMP_DIR"

# Restauration de la base de données
echo "🗄️  Restauration de la base de données..."
docker-compose up -d db
sleep 10

# Attendre que PostgreSQL soit prêt
while ! docker-compose exec db pg_isready -U ${DB_USER:-payroll_user}; do
    echo "⏳ Attente de PostgreSQL..."
    sleep 2
done

# Restauration de la base de données
docker-compose exec -T db psql -U ${DB_USER:-payroll_user} -d ${DB_NAME:-payroll_db} < $TEMP_DIR/payroll_backup_*_database.sql

# Restauration des fichiers média
echo "📁 Restauration des fichiers média..."
if [ -f $TEMP_DIR/payroll_backup_*_media.tar.gz ]; then
    tar -xzf $TEMP_DIR/payroll_backup_*_media.tar.gz
else
    echo "⚠️  Fichiers média non trouvés dans la sauvegarde"
fi

# Restauration des fichiers de configuration
echo "⚙️  Restauration des fichiers de configuration..."
if [ -f $TEMP_DIR/payroll_backup_*_config.tar.gz ]; then
    tar -xzf $TEMP_DIR/payroll_backup_*_config.tar.gz
    echo "📝 Fichiers de configuration restaurés"
else
    echo "⚠️  Fichiers de configuration non trouvés dans la sauvegarde"
fi

# Nettoyage
rm -rf "$TEMP_DIR"

# Redémarrage des services
echo "🚀 Redémarrage des services..."
docker-compose up -d

# Vérification
echo "🔍 Vérification de la restauration..."
sleep 10
docker-compose ps

echo "🎉 Restauration terminée avec succès!"
echo "📊 Application: http://localhost:8000"
echo "🔧 Administration: http://localhost:8000/admin/"
