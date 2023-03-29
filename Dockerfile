FROM python

WORKDIR /project

COPY . .

RUN /bin/bash ./installing

CMD ["python3", "./async_main.py"]
