FROM python:3

WORKDIR /workdir

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN rm requirements.txt