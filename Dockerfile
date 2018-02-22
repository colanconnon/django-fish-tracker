FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
ADD requirements.txt /src/
RUN pip install -r requirements.txt
ADD . /src/
CMD /usr/local/bin/gunicorn -w 3 -b :80 --timeout 300 --worker-class=meinheld.gmeinheld.MeinheldWorker FishTrackerDjango.wsgi:application
