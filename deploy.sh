#!/bin/bash
# deploy app

test_host="tilefy.local"

function rebuild_test {
    echo "rebuild testing environment"
    ssh "$test_host" 'mkdir -p {docker/volume/tilefy/data/fonts,docker/volume/tilefy/data/logos}'
    rsync -a --progress --delete-after \
        --exclude ".git" \
        --exclude ".gitignore" \
        --exclude "**/cache" \
        --exclude "**/__pycache__/" \
        --exclude "db.sqlite3" \
        . -e ssh "$test_host":tilefy

    rsync -a --progress --delete-after custom_logos/* "$test_host":docker/volume/tilefy/data/logos
    rsync -a --progress --delete-after custom_fonts/* "$test_host":docker/volume/tilefy/data/fonts
    rsync --progress --ignore-existing docker-compose.yml -e ssh "$test_host":docker
    rsync --progress tiles.example.yml -e ssh "$test_host":docker/volume/tilefy/data/tiles.yml

    ssh "$test_host" "docker buildx build --build-arg INSTALL_DEBUG=1 -t bbilly1/tilefy tilefy --load"
    ssh "$test_host" 'docker compose -f docker/docker-compose.yml up -d --build'
}

function validate {

    if [[ $1 ]]; then
        check_path="$1"
    else
        check_path="."
    fi

    echo "run validate on $check_path"

    echo "running black"
    black --diff --color --check -l 79 "$check_path"
    echo "running codespell"
    codespell --skip="./.git" "$check_path"
    echo "running flake8"
    flake8 "$check_path" --count --max-complexity=10 --max-line-length=79 \
        --show-source --statistics
    echo "running isort"
    isort --check-only --diff --profile black -l 79 "$check_path"
    printf "    \n> all validations passed\n"

}

function docker_publish {

    # check things
    if [[ $(git branch --show-current) != 'master' ]]; then
        echo 'you are not on master, dummy!'
        return
    fi

    if [[ $(systemctl is-active docker) != 'active' ]]; then
        echo "starting docker"
        sudo systemctl start docker
    fi
    echo "latest tags:"
    git tag | tail -n 5 | sort -r

    printf "\ncreate new version:\n"
    read -r VERSION

    echo "build and push $VERSION?"
    read -rn 1

    # start build
    sudo docker buildx build \
        --platform linux/amd64,linux/arm64 \
        -t bbilly1/tilefy \
        -t bbilly1/tilefy:"$VERSION" \
        -t bbilly1/tilefy:unstable --push .

    # create release tag
    echo "commits since last version:"
    git log "$(git describe --tags --abbrev=0)"..HEAD --oneline
    git tag -a "$VERSION" -m "new release version $VERSION"
    git push all "$VERSION"

}

# publish unstable tag to docker
function sync_unstable {

    if [[ $(systemctl is-active docker) != 'active' ]]; then
        echo "starting docker"
        sudo systemctl start docker
    fi

    # start amd64 build
    sudo docker buildx build \
        --platform linux/amd64 \
        -t bbilly1/tilefy:unstable --push .

}


if [[ $1 == "test" ]]; then
    rebuild_test
elif [[ $1 == "validate" ]]; then
    # check package versions in requirements.txt for updates
    python version_check.py
    validate "$2"
elif [[ $1 == "docker" ]]; then
    docker_publish
elif [[ $1 == "unstable" ]]; then
    sync_unstable
else
    echo "valid options are: test | docker | unstable"
fi

##
exit 0
