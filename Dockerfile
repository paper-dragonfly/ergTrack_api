FROM ubuntu 

#install stuff
RUN apt update
RUN apt install -y python3
RUN apt install -y python3-pip 
RUN apt install -y python3.10-venv
COPY requirements.txt .
RUN pip install -r requirements.txt 
# RUN apt install -y postgresql postgresql-contrib
# RUN systemctl start postgresql.service

#add files
WORKDIR kaja
RUN mkdir -p ./src
RUN mkdir -p ./tests
RUN mkdir -p ./config 
COPY src src 
# COPY config.yaml config
COPY README.md .
COPY tests tests
COPY pyproject.toml . 
COPY setup.cfg . 

#build project into package
RUN python3 -m pip install --upgrade build
RUN python3 -m build
RUN python3 -m pip install -e . --no-deps

#run app
EXPOSE 5000
CMD python3 src/ergtrack_api/app.py
# myIP: --add-host=Nicos-MacBook-Pro.local:192.168.1.6. 

