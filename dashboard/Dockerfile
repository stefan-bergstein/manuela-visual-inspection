FROM registry.access.redhat.com/ubi8/ubi

RUN yum install -y python3; yum clean all

COPY ./static /app/static
COPY ./templates /app/templates
COPY *.* /app/

WORKDIR /app
RUN python3 -m pip install -r requirements.txt

EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["dashboard.py"]