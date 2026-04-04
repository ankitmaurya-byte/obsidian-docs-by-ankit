# Commands
``` 
docker_cli:

  basics:
    docker_version:
      command: docker --version
      description: Show installed Docker version

    docker_info:
      command: docker info
      description: Detailed system info (containers, images, storage, runtime)

    docker_help:
      command: docker help
      description: List all available Docker commands

  images:
    build:
      command: docker build -t <name:tag> .
      description: Build image from Dockerfile
      flags:
        - -t: Assign tag (name:version)
        - -f: Specify Dockerfile path
        - --no-cache: Disable cache
        - --build-arg: Pass build-time variables

    list:
      command: docker images
      description: List all images

    remove:
      command: docker rmi <image_id>
      description: Remove image

    pull:
      command: docker pull <image>
      description: Download image from registry

    push:
      command: docker push <repo/image>
      description: Upload image to registry

    tag:
      command: docker tag <image> <repo/image:tag>
      description: Tag image for pushing

    inspect:
      command: docker inspect <image_id>
      description: View detailed metadata of image

    history:
      command: docker history <image>
      description: Show image layers history

  containers:
    run:
      command: docker run [OPTIONS] <image>
      description: Create and start container
      common_flags:
        - -d: Run in background (detached)
        - -it: Interactive terminal
        - -p: Port mapping (host:container)
        - --name: Assign container name
        - -e: Set environment variable
        - -v: Mount volume
        - --rm: Auto-remove after stop

    list_running:
      command: docker ps
      description: Show running containers

    list_all:
      command: docker ps -a
      description: Show all containers

    stop:
      command: docker stop <container_id>
      description: Stop running container

    start:
      command: docker start <container_id>
      description: Start stopped container

    restart:
      command: docker restart <container_id>
      description: Restart container

    remove:
      command: docker rm <container_id>
      description: Delete container

    rename:
      command: docker rename <old> <new>
      description: Rename container

  exec_and_logs:
    exec_shell:
      command: docker exec -it <container_id> bash
      description: Open shell inside running container

    exec_command:
      command: docker exec <container_id> <cmd>
      description: Run command inside container

    logs:
      command: docker logs <container_id>
      description: Show container logs

    logs_follow:
      command: docker logs -f <container_id>
      description: Stream logs in real time

  volumes:
    list:
      command: docker volume ls
      description: List volumes

    create:
      command: docker volume create <name>
      description: Create volume

    inspect:
      command: docker volume inspect <name>
      description: View volume details

    remove:
      command: docker volume rm <name>
      description: Delete volume

  networks:
    list:
      command: docker network ls
      description: List networks

    create:
      command: docker network create <name>
      description: Create network

    inspect:
      command: docker network inspect <name>
      description: View network details

    connect:
      command: docker network connect <network> <container>
      description: Connect container to network

    disconnect:
      command: docker network disconnect <network> <container>
      description: Disconnect container from network

  system_cleanup:
    container_prune:
      command: docker container prune
      description: Remove stopped containers

    image_prune:
      command: docker image prune
      description: Remove unused images

    volume_prune:
      command: docker volume prune
      description: Remove unused volumes

    system_prune:
      command: docker system prune -a
      description: Remove all unused data (containers, images, networks)

  stats_and_inspect:
    stats:
      command: docker stats
      description: Live CPU, memory usage

    inspect_container:
      command: docker inspect <container_id>
      description: Detailed container info (JSON)

    top:
      command: docker top <container_id>
      description: Show running processes inside container

  registry_auth:
    login:
      command: docker login
      description: Login to Docker Hub

    logout:
      command: docker logout
      description: Logout from Docker Hub

  save_load:
    save:
      command: docker save -o file.tar <image>
      description: Save image to tar file

    load:
      command: docker load -i file.tar
      description: Load image from tar file

  docker_compose_v2:
    up:
      command: docker compose up
      description: Start services

    up_build:
      command: docker compose up --build
      description: Build and start services

    up_detached:
      command: docker compose up -d
      description: Run in background

    down:
      command: docker compose down
      description: Stop and remove services

    logs:
      command: docker compose logs
      description: View logs

    logs_follow:
      command: docker compose logs -f
      description: Follow logs

    exec:
      command: docker compose exec <service> bash
      description: Run command inside service container

```
