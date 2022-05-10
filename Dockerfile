FROM continuumio/miniconda3

# The environment variable ensures that the python output is set straight
# to the terminal without buffering it first
ENV PYTHONUNBUFFERED 1

WORKDIR /

COPY ./requirements.txt app/

WORKDIR /app

RUN conda create --name dst python=3.7

RUN conda install --channel conda-forge cartopy

RUN pip install -r requirements.txt

WORKDIR /

COPY . app

WORKDIR /app

EXPOSE 5006

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "dst", "python", "decision-support-tool.py"]
#, "--session-token-expiration", "86400", "--prefix", "building-dst", "--use-xheaders", "--log-level=debug"]
