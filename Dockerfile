FROM python:3.10.4-alpine

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG PROJECT_NAME=kerani
ARG USERNAME=$PROJECT_NAME
ARG GROUP=$PROJECT_NAME
ARG CODE_DIR=/$PROJECT_NAME

RUN apk update && \
        apk add sudo && \
        apk add bash && \
        apk add --virtual .build-deps gcc musl-dev libffi-dev binutils libc-dev curl && \
        apk add python3-dev zlib-dev && \
        apk add build-base

RUN addgroup -g 1000 -S $GROUP \
    && adduser -D --uid 1000 -S -G $USERNAME $GROUP \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && mkdir -p $CODE_DIR \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    && chown -R $USERNAME:$GROUP $CODE_DIR

WORKDIR $CODE_DIR

# Install dependencies
COPY --chown=$USERNAME:$GROUP requirements-dev.txt $CODE_DIR/

RUN pip install -r requirements.txt
RUN apk --purge del .build-deps

USER $USERNAME

COPY --chown=$USERNAME:$GROUP . $CODE_DIR
