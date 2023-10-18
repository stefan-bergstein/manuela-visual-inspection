FROM registry.access.redhat.com/ubi9/ubi

#RUN dnf install -y python3 python3-devel gcc gcc-c++ && dnf clean all

RUN dnf install -y python3 pip && dnf clean all

RUN mkdir /app
WORKDIR /app
COPY *.* /app/

RUN pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

USER 1001

EXPOSE 8080
ENTRYPOINT ["python3"]
CMD ["image-processor.py"]