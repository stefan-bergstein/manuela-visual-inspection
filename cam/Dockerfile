FROM registry.access.redhat.com/ubi8/ubi

RUN yum install -y python3; yum clean all
RUN python3 -m pip install --upgrade pip

WORKDIR /app
COPY ./ /app/
RUN python3 -m pip install -r requirements.txt

EXPOSE 8088
ENTRYPOINT ["python3"]
CMD ["client.py", "-l", "INFO", "--fps", "0.5", "--scale", "0.5", "--images"]