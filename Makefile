start all:
	docker start rashideveloper
	docker start infallible_northcutt
	celery -A apps worker --beat

mig:
	./manage.py makemigrations
	./manage.py migrate