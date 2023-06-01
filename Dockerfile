FROM python:3.9

COPY . .

ENV VIRTUAL_ENV=/venv

RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -r /requirements.txt

WORKDIR /.

ENV STOP=true
ENV STEPS=1000

ENV PYTHONPATH=/.
RUN sed -i 's/\r$//' /run.sh
RUN chmod a+x /run.sh
CMD /bin/bash -c "source /run.sh $STEPS $STOP"