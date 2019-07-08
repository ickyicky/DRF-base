FROM project/project-server-base:devel

ENV DJANGO_SETTINGS_MODULE project.settings

RUN mkdir /log
RUN echo "" > /log/debug.log
RUN chmod +rw /log/debug.log

WORKDIR /app

COPY setup.py /app
RUN python setup.py develop

COPY . /app
RUN ./bin/collectstatic-nosettings.py --env-file ../.env

CMD ["gunicorn", "project.wsgi", "--bind", "0.0.0.0:80", "--workers", "2", "--worker-class", "gevent", "--access-logfile=-"]
