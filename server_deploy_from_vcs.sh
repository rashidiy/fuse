#Requirements
# 1. git@gitlab.com:username/project.git
# 2. must be exists requirements.txt
# 3. user's username must be ubuntu in server
# 4. Django Root Dir's name must be project
# 5. Git(lab/hub, ***) ssh key

# Getting project variables
project_url=$1  # git url
project_name=$2 # project name
domain=$3       # domain
project_port=$4 # port

# Allow Given Post
ufw allow $project_port

cd /var/www/
mkdir $project_name

# Clone from Git
git clone $project_url ./$project_name
cd project_name

# Activate venv
python3 -m venv venv
source venv/bin/activate

# Install Requirements
pip3 install weel
pip3 install gunicorn
pip3 install -r requirements.txt
pip3 manage.py collectstatic --no-input

# Create nginx file
cat >/etc/nginx/sites-available/$project_name <<EOL
server {
    listen ${project_port};
    #server_name $domain;

    # location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /var/www/${project_name};
    }

    location /media/ {
        root /var/www/${project_name};
    }

    location / {
        include         proxy_params;
        proxy_pass      http://unix:/var/www/${project_name}/${project_name}.sock;
    }
}
EOL

# Create soft link
ln -s /etc/nginx/sites-available/$project_name /etc/nginx/sites-enabled/

# Gunicorn settings
cat >/etc/systemd/system/$project_name.service <<EOL
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/${project_name}
ExecStart=/var/www/${project_name}/venv/bin/gunicorn --workers 3 --bind unix:/var/www/${project_name}/${project_name}.sock root.wsgi:application

[Install]
WantedBy=multi-user.target
EOL
# Start service(background-process)
systemctl start ${project_name}.service
systemctl enable ${project_name}.service
systemctl restart ${project_name}.service

# Restart nginx
systemctl restart nginx
# shellcheck disable=SC2086
