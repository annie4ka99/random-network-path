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
RUN chmod a+x /run.sh
CMD /run.sh $STEPS $STOP