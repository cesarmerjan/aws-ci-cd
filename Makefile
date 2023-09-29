.PHONY: build-image
build-image:
	docker build -t test:0.0.1 \
	-f ./Dockerfile .
	docker tag test:0.0.1 test:latest


.PHONY: server
server:
	docker run -it --name api -p 5000:5000 --rm test:latest ./run_server.sh


.PHONY: server-debug
server-debug:
	python run.py

.PHONY: admin-user
admin-user:
	docker run --name create-admin --rm test:latest python -m flask --app run:app user create admin admin@admin.com hardToGu3sS


.PHONY: docker-login
docker-login:
	aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 863121614725.dkr.ecr.us-east-1.amazonaws.com


.PHONY: push-image
push-image: build-image docker-login
	docker tag test:latest 863121614725.dkr.ecr.us-east-1.amazonaws.com/test:latest
	docker push 863121614725.dkr.ecr.us-east-1.amazonaws.com/test:latest

.PHONY: database-ui
database-ui:
	docker run --name pgadmin -e PGADMIN_DEFAULT_PASSWORD=password -e PGADMIN_DEFAULT_EMAIL=admin@admin.com -p 5050:80 --rm dpage/pgadmin4
