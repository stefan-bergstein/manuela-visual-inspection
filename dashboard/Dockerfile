FROM registry.access.redhat.com/ubi8/ubi

RUN dnf install -y python3 python3-devel gcc gcc-c++ && dnf clean all

COPY ./static /app/static
COPY ./templates /app/templates
COPY *.* /app/

WORKDIR /app
RUN python3 -m pip install -r requirements.txt

EXPOSE 8088
ENTRYPOINT ["python3"]
CMD ["dashboard.py"]