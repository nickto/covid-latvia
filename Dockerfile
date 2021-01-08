FROM python:3.8 AS common
COPY . /app
WORKDIR /app

FROM common as data
RUN pip install --no-cache-dir -r requirements/data.txt
ENTRYPOINT [ "python" ]

FROM common as dashboard
RUN pip install --no-cache-dir -r requirements/dashboard.txt
ENTRYPOINT [ "dashboard" ]
CMD [ "run", "dashboard/main.py" ]