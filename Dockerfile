FROM python:3.7.6

RUN pip install uvloop

WORKDIR /server
COPY ./src /server
COPY httpd.conf /etc/httpd.conf

EXPOSE 80
CMD python3 master.py