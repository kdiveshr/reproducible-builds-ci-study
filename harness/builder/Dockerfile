# Builder image for the cross-environment reproducibility study.
#
# One Dockerfile, one tag, used in all three environments (GitHub Actions,
# GitLab CI, local Docker). The toolchain is fixed here so that any
# cross-environment artifact diff is leakage from the CI environment itself
# (checkout path, runner env vars, filesystem), not from the toolchain.
#
# Architecture note: this image is built for linux/amd64 and linux/arm64 from
# the same Dockerfile. The arch-native digest is recorded per environment in
# each build record; "identical builder image" means identical Dockerfile,
# JDK/Maven versions, and tag.
#
# Locale is fixed inside the image (C.UTF-8); TZ is left at the container
# default (UTC). Runner locale/timezone settings are NOT passed into the
# container, so they cannot leak into builds.
FROM maven:3.9.9-eclipse-temurin-17

RUN apt-get update \
    && apt-get install -y --no-install-recommends git python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && git --version \
    && python3 --version \
    && mvn -version \
    && java -version

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

WORKDIR /src
