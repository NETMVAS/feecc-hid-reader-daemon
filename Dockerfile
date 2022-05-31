FROM python:3.10
WORKDIR /src
COPY ./requirements.txt /src/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /src/requirements.txt
COPY ./EventToInternet /src/EventToInternet
COPY ./async_executor.py /src/
CMD ["python3", "async_executor.py"]
