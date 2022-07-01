FROM alpine:3.10

#ARG terraform_version="0.12.5"
ARG terraform_version="1.2.3"

# Install terraform etc
RUN apk update --no-cache \
    && apk add --no-cache \
        wget \
        unzip \
        curl \
    && wget https://releases.hashicorp.com/terraform/${terraform_version}/terraform_${terraform_version}_linux_amd64.zip \
    && unzip ./terraform_${terraform_version}_linux_amd64.zip -d /usr/local/bin/ \
    && rm -rf ./terraform_${terraform_version}_linux_amd64.zip

WORKDIR /.ssh    
WORKDIR /terraform/aws
