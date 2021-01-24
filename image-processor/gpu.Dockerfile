FROM tensorflow/tensorflow:2.3.0-gpu

RUN mkdir /app

WORKDIR /app

RUN curl -LO https://github.com/stefan-bergstein/manuela-visual-inspection/releases/download/v0.1-alpha-tf/tf-model.tar \
    && tar xvf tf-model.tar --no-same-owner && rm -f tf-model.tar

COPY ./ /app/
RUN python3 -m pip install -r requirements.txt 

User 1001

ENTRYPOINT ["python3"]
CMD ["image-processor.py"]