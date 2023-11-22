FROM python:3-alpine

COPY * /service/
WORKDIR /service
RUN pip3 install -r requirements.txt

CMD python3 carbon-aware-service.py
