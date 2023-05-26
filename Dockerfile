FROM python:3.9

COPY . /network-api/

ENV VIRTUAL_ENV=/network-api/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r /network-api/requirements.txt

WORKDIR /network-api/

EXPOSE 8080

CMD [ "python", "/network-api/network_application.py", "--input=input.txt", "--log=env.log", "--seed=0", "--host=0.0.0.0", "--port=8080" ]