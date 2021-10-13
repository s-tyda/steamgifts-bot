FROM python:3.7
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["cli.py"]
ENTRYPOINT ["python3"]