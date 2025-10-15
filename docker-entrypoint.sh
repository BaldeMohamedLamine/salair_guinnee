#!/bin/bash

# Script de démarrage pour le conteneur Docker
set -e

echo "🚀 Démarrage du système de paie Guinée..."

# Attendre que la base de données soit prête
echo "⏳ Attente de la base de données..."
while ! pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "Base de données non disponible - attente..."
  sleep 2
done

echo "✅ Base de données disponible!"

# Exécuter les migrations
echo "🔄 Exécution des migrations..."
python manage.py migrate --settings=payroll_project.settings_production

# Collecter les fichiers statiques
echo "📦 Collecte des fichiers statiques..."
python manage.py collectstatic --noinput --settings=payroll_project.settings_production

# Créer un superutilisateur si nécessaire (optionnel)
echo "👤 Vérification du superutilisateur..."
python manage.py shell --settings=payroll_project.settings_production << EOF
from salary.models import User
if not User.objects.filter(is_superuser=True).exists():
    print("Aucun superutilisateur trouvé. Créez-en un avec:")
    print("python manage.py createsuperuser --settings=payroll_project.settings_production")
else:
    print("Superutilisateur existant trouvé.")
EOF

# Créer l'instance Company si nécessaire
python manage.py shell --settings=payroll_project.settings_production << EOF
from salary.models import Company
company = Company.get_company()
print(f"Entreprise configurée: {company.name}")
EOF

echo "🎉 Système de paie prêt!"
echo "📊 Accédez à l'application sur: http://localhost:8000"
echo "🔧 Interface d'administration: http://localhost:8000/admin/"

# Démarrer le serveur
exec "$@"
