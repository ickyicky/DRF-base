FROM project/api-base

ENV DJANGO_SETTINGS_MODULE api.settings

RUN mkdir /opt/app/log

ARG version
ARG appname
ARG project
ARG appversion
LABEL bsp_project=$project \
      bsp_appname=$api \
      bsp_version=$version

WORKDIR /opt/app

COPY setup.py /opt/app
RUN python3 setup.py develop --user

COPY . /opt/app
RUN ./bin/collectstatic-nosettings.py --env-file ../.env

CMD ["gunicorn", "api.wsgi", "--bind", "0.0.0.0:8080", "--workers", "4", "--worker-class", "gevent", "--reload", "--access-logfile=-"]