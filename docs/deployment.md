# Deployment

To deploy to production server:

1. Stop the running containers
  ```shell
  docker exec osmaxx-starter /usr/local/bin/docker-compose stop
  ```

2. Rename the old source and clone the repository master branch without history:

  ```shell
  git clone --depth 1 -b master https://github.com/geometalab/osmaxx.git osmaxx && cd osmaxx
  git submodule init && git submodule update
  ```
  Repository details see [Project repository](git-repository.md).
3. Link production configuration for docker-compose, Details see [Docker container bootstrapping](../README.md#initializationdocker-container-bootstrapping).
4. Add target specific environment variables to compose-production.yml
  * If you are using an nginx proxy (jwilder/nginx-proxy), you need to set the environment variable
    `VIRTUAL_HOST=osmaxx.yourdomain.tld`
5. Build the containers. Use docker-compose container instead of native installation:

  a. Create the docker-compose container if not already exists:
    ```shell
    # "up" && "--no-recreate": default arguments used by the systemd service starter
    docker create \
      --name osmaxx-starter
      -v "/path/to/source/repo:/app" \
      -v "/var/run/docker.sock:/var/run/docker.sock" \
      -e "COMPOSE_PROJECT_NAME=osmaxx" \
      "dduportal/docker-compose:1.3.1" up --no-recreate
    ```

  b. Pull images & build osmaxx containers:  
    ```shell
    # pull newest images
    # "--rm" removes the temporary used compose-container
    docker run -v "/path/to/source/repo:/app" -v "/var/run/docker.sock:/var/run/docker.sock" -e "COMPOSE_PROJECT_NAME=osmaxx" --rm "dduportal/docker-compose:1.3.1" pull

    # build own containers
    docker run -v "/path/to/source/repo:/app" -v "/var/run/docker.sock:/var/run/docker.sock" -e "COMPOSE_PROJECT_NAME=osmaxx" --rm "dduportal/docker-compose:1.3.1" build
    ```

6. Run migrations and add create super user, Details see [Docker container bootstrapping](../README.md#initializationdocker-container-bootstrapping).
  For docker-compose container run:

  ```shell
  # database needs to be running before the webapp container
  docker run -v "/path/to/source/repo:/app" -v "/var/run/docker.sock:/var/run/docker.sock" -e "COMPOSE_PROJECT_NAME=osmaxx" --rm "dduportal/docker-compose:1.3.1" up -d database

  # apply migrations
  # "-it" is needed to get an interactive terminal
  # "run --rm" removes the temporary used webapp container
  docker run -v "/path/to/source/repo:/app" -v "/var/run/docker.sock:/var/run/docker.sock" -e "COMPOSE_PROJECT_NAME=osmaxx" -it --rm "dduportal/docker-compose:1.3.1" run --rm webapp /bin/bash -c "python3 manage.py migrate && python3 manage.py createsuperuser"

  # stop running containers
  docker run -v "/path/to/source/repo:/app" -v "/var/run/docker.sock:/var/run/docker.sock" -e "COMPOSE_PROJECT_NAME=osmaxx" --rm "dduportal/docker-compose:1.3.1" stop
  ```
7. Load data container content from old container if there is one, Details see [Useful Docker commands](project-development-environment.md#useful-docker-commands).
8. Load database container content from old container if there is one, Details see [Useful Docker commands](project-development-environment.md#useful-docker-commands).
9. Add a system startup script running `docker-compose up`
  E.g. /etc/systemd/system/osmaxx.service:

  ```shell
  [Unit]
  Description=Start osmaxx application

  [Service]
  ExecStart=/usr/bin/docker start -a osmaxx-starter
  ExecStop=/usr/bin/docker exec osmaxx-starter /usr/local/bin/docker-compose stop --timeout 60
  ExecStop=/usr/bin/docker kill --signal=INT osmaxx-starter
  ExecStop=/usr/bin/docker stop -t 10 osmaxx-starter
  Restart=always

  [Install]
  WantedBy=multi-user.target
  ```
  **important**: osmax-starter container needs to be created before!

  "/usr/bin/docker start -a osmaxx-starter" will use the default arguments configured on create.

1. Enable startup service  
  ```shell
  sudo systemctl enable docker-osmaxx.service
  ```

11. Start the containers
  ```shell
  sudo systemctl start docker-osmaxx.service
  ```