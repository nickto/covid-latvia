FROM python:3.8
COPY . /app
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT [ "streamlit" ]
CMD [ "run", "dashboard/main.py" ]