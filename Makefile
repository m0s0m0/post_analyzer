build_local:
	docker-compose -f ./docker/docker-compose.local.yml build


build_local_no_cache:
	docker-compose -f ./docker/docker-compose.local.yml build --no-cache
 

up_local:
	docker-compose -f ./docker/docker-compose.local.yml up