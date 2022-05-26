FROM python:3.10.4

WORKDIR /facies_classification

# ENV VIRTUAL_ENV=/opt/venv
# RUN python3 -m venv $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY requirements.txt ./requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8501

COPY . /facies_classification/

ENTRYPOINT ["streamlit", "run"]

CMD ["app.py"]
