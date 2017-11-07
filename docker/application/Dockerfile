FROM php:7.1-fpm

# gosu
ENV GOSU_VERSION 1.10
RUN set -ex; \
    \
    fetchDeps=' \
        ca-certificates \
        wget \
    '; \
    apt-get -q update; \
    apt-get install -y --no-install-recommends $fetchDeps; \
    \
    dpkgArch="$(dpkg --print-architecture | awk -F- '{ print $NF }')"; \
    wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch"; \
    wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$dpkgArch.asc"; \
    \
    export GNUPGHOME="$(mktemp -d)"; \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4; \
    gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu; \
    rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc; \
    \
    chmod +x /usr/local/bin/gosu; \
    gosu nobody true

RUN apt-get -qy update --fix-missing

# Composer installation.
RUN curl -sS https://getcomposer.org/installer | php \
        && mv composer.phar /usr/bin/composer

# Add Node Repos
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -

# OS Packages
RUN apt-get -q update && \
    apt-get -y install unzip \
                       git \
                       vim \
                       libicu-dev \
                       libmcrypt-dev \
                       libxml2-dev \
                       zlib1g-dev \
                       libpq-dev \
                       nodejs \
                       python3 \
                       gettext-base \
                       libmagickwand-dev

RUN pecl install apcu xdebug imagick && \
    docker-php-ext-enable apcu \
                          xdebug  \
                          imagick && \
    docker-php-ext-configure bcmath && \
    docker-php-ext-install pdo \
                           pdo_pgsql \
                           intl \
                           mbstring \
                           mcrypt \
                           zip \
                           bcmath \
                           soap

RUN apt-get clean; rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /usr/share/doc/*

RUN useradd -ms /bin/bash application
RUN mkdir /code && \
    chown -R application: /code

USER application
WORKDIR /home/application
RUN composer global require "fxp/composer-asset-plugin:^1.4.1"

USER root
ENV PATH /code/vendor/bin:${PATH}

WORKDIR /usr/local/etc/php-fpm.d
RUN rm www.conf
ADD usergroup.conf usergroup.conf.default

WORKDIR /docker
ADD entrypoint.py .
RUN chmod a+x entrypoint.py
ENTRYPOINT ["/docker/entrypoint.py"]
CMD ["serve"]

WORKDIR /code
