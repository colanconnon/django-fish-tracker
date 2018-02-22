This app is built with django and deployed with docker compose


# Running the app
First build containers

`docker-compose build`

run the app

`docker-compose up -d`

exec into the container

`docker-compose exec web bash`

run migrations

`python3 manage.py migrate`

visit localhost:80 to see the running app
