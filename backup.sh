#!/bin/bash

# Script de sauvegarde pour le système de paie Guinée
set -e

echo "💾 Sauvegarde du système de paie Guinée"
echo "======================================"

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="payroll_backup_$DATE"

# Création du répertoire de sauvegarde
mkdir -p $BACKUP_DIR

echo "📦 Création de la sauvegarde: $BACKUP_NAME"

# Sauvegarde de la base de données
echo "🗄️  Sauvegarde de la base de données..."
docker-compose exec -T db pg_dump -U ${DB_USER:-payroll_user} ${DB_NAME:-payroll_db} > $BACKUP_DIR/${BACKUP_NAME}_database.sql

# Sauvegarde des fichiers média
echo "📁 Sauvegarde des fichiers média..."
if [ -d "media" ]; then
    tar -czf $BACKUP_DIR/${BACKUP_NAME}_media.tar.gz media/
else
    echo "⚠️  Répertoire media non trouvé"
fi

# Sauvegarde des fichiers de configuration
echo "⚙️  Sauvegarde des fichiers de configuration..."
tar -czf $BACKUP_DIR/${BACKUP_NAME}_config.tar.gz .env docker-compose.yml nginx.conf

# Création d'une archive complète
echo "📦 Création de l'archive complète..."
tar -czf $BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz \
    $BACKUP_DIR/${BACKUP_NAME}_database.sql \
    $BACKUP_DIR/${BACKUP_NAME}_media.tar.gz \
    $BACKUP_DIR/${BACKUP_NAME}_config.tar.gz

# Nettoyage des fichiers temporaires
rm $BACKUP_DIR/${BACKUP_NAME}_database.sql
rm $BACKUP_DIR/${BACKUP_NAME}_media.tar.gz
rm $BACKUP_DIR/${BACKUP_NAME}_config.tar.gz

echo "✅ Sauvegarde terminée: $BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz"

# Affichage de la taille de la sauvegarde
echo "📊 Taille de la sauvegarde:"
ls -lh $BACKUP_DIR/${BACKUP_NAME}_complete.tar.gz

# Nettoyage des anciennes sauvegardes (garde les 7 dernières)
echo "🧹 Nettoyage des anciennes sauvegardes..."
cd $BACKUP_DIR
ls -t payroll_backup_*_complete.tar.gz | tail -n +8 | xargs -r rm
cd ..

echo "🎉 Sauvegarde terminée avec succès!"
