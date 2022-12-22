'''


/etc/nginx/sites-enabled/fuse

server {
    listen       8000;
    server_name  217.18.62.222;

    location = /favicon.ico { accesscd_log off; log_not_found off; }

    location /static/ {
        root /root/DJANGO/fuse;
    }

    location /media/ {
        root /root/DJANGO/fuse;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/root/DJANGO/fuse/fuse_sock.sock;
    }

}




/etc/systemd/system/fuse.service


[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/root/DJANGO/fuse
ExecStart=/root/DJANGO/fuse/venv/bin/gunicorn --workers 3 --bind unix:/root/DJANGO/fuse/fuse_sock.sock root.wsgi:application

[Install]
WantedBy=multi-user.target



systemctl start (service_fayl_nomi).service
systemctl enable (service_fayl_nomi).service





'''