FROM apache/airflow:2.8.2

ENV AIRFLOW_HOME=/opt/airflow 
USER $AIRFLOW_UID

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# set up bash and cli tools
USER root 
RUN apt-get update -qq && apt-get install vim -qqq && apt-get install unzip
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# set up AWS cli
ENV AWS_HOME=/home/aws
RUN TMP_DIR="$(mktemp -d)" \ 
 && curl -fL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "${TMP_DIR}/awscliv2.zip" \
 && unzip "${TMP_DIR}/awscliv2.zip" -d "${AWS_HOME}" \
 && sudo "${AWS_HOME}/aws/install" \
 && rm -rf "${TMP_DIR}" \
 && aws --version

WORKDIR $AIRFLOW_HOME
USER $AIRFLOW_UID