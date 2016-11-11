FROM python:2.7-onbuild

RUN mkdir /data && \
  rm /usr/src/app/hourcounter.db && \
  ln -s /data/hourcounter.db /usr/src/app/hourcounter.db

VOLUME /data
EXPOSE 8080
ENV FLASK_APP main.py
CMD [ "flask", "run", "--host=0.0.0.0", "--port=8080" ]
