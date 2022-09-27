FROM ubuntu 
WORKDIR kaja
RUN mkdir -p ./src
RUN mkdir -p ./src/api 
RUN mkdir -p ./tests
RUN mkdir -p ./config 
COPY src src 
COPY requirements.txt .
COPY post_classes.py .
COPY config .
COPY tests tests
COPY initialize_db.py . 
RUN apt update
RUN apt install -y python3
# RUN apt install -y postgresql-client
RUN apt install -y python3-pip 
RUN python3 -m pip install --upgrade build
RUN pip install -r requirements.txt 
RUN python3 -m build
RUN python3 -m pip install -e . --no-deps
CMD gunicorn src.app:app
# --add-host=host:192.168.1.6.

