NAME   := tristanbrown/crontris
TAG    := $(shell git rev-parse --short HEAD)
BRANCH := $(shell git rev-parse --abbrev-ref HEAD)
IMG    := ${NAME}:${TAG}
LATEST := ${NAME}:${BRANCH}
 
build:
	@docker build -t ${IMG} .
	@docker tag ${IMG} ${LATEST}
 
push:
	@docker push ${NAME}
 
login:
	@docker log -u ${DOCKER_USER} -p ${DOCKER_PASS}
