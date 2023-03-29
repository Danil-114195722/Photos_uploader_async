build:
	sudo docker build -t load_photo .
run:
	sudo docker run -d --rm --name load_app load_photo
start:
	sudo docker start load_app
stop:
	sudo docker stop load_app
