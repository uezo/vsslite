FROM python:3.11.6

RUN apt-get update
RUN apt-get install -y liblapack-dev

RUN pip install --upgrade pip
RUN pip install vsslite

ENV API_KEY YOUR_API_KEY
ENV DATA_PATH /data/vss.db

EXPOSE 8000
CMD ["python", "-m", "vsslite"]
