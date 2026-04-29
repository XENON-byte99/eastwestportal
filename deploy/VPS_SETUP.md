# ============================================================
# EastWest Portal — VPS Server Setup Guide
# Target: eee.firebaseit.com (Hostinger VPS)
# ============================================================

## STEP 1: SSH into your VPS
ssh root@YOUR_VPS_IP

## STEP 2: Install system packages
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv git nginx mysql-server

## STEP 3: Create project directory and clone your GitHub repo
mkdir -p /var/www/eastwestportal
cd /var/www/eastwestportal
git clone https://github.com/YOUR_GITHUB_USERNAME/eastwestportal.git .

## STEP 4: Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## STEP 5: Create MySQL database
mysql -u root -p << 'EOF'
CREATE DATABASE ewportal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ewportal_user'@'localhost' IDENTIFIED BY 'STRONG_DB_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON ewportal_db.* TO 'ewportal_user'@'localhost';
FLUSH PRIVILEGES;
EOF

## STEP 6: Create .env on the server
nano /var/www/eastwestportal/.env
# Paste the contents of .env.production and fill in values:
#   SECRET_KEY=<generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
#   DEBUG=False
#   ALLOWED_HOSTS=eee.firebaseit.com,localhost,127.0.0.1
#   DB_ENGINE=django.db.backends.mysql
#   DB_NAME=ewportal_db
#   DB_USER=ewportal_user
#   DB_PASSWORD=STRONG_DB_PASSWORD_HERE
#   DB_HOST=127.0.0.1
#   DB_PORT=3306
#   CSRF_TRUSTED_ORIGINS=https://eee.firebaseit.com

## STEP 7: Run initial Django setup
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser

## STEP 8: Set up Gunicorn systemd service
# Copy the gunicorn service file:
cp /var/www/eastwestportal/deploy/gunicorn_ewportal.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable gunicorn_ewportal
systemctl start gunicorn_ewportal

## STEP 9: Set up Nginx
cp /var/www/eastwestportal/deploy/nginx_ewportal.conf /etc/nginx/sites-available/eastwestportal
ln -s /etc/nginx/sites-available/eastwestportal /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

## STEP 10: Set file permissions
chown -R www-data:www-data /var/www/eastwestportal/media
chmod -R 755 /var/www/eastwestportal

## STEP 11: Add GitHub Secrets for auto-deploy
# In your GitHub repo → Settings → Secrets and Variables → Actions
# Add these 4 secrets:
#   VPS_HOST     = YOUR_VPS_IP_ADDRESS
#   VPS_USER     = root  (or your sudo user)
#   VPS_PASSWORD = YOUR_VPS_ROOT_PASSWORD
#   VPS_PORT     = 22
