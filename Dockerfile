FROM python:3.8-bullseye
RUN addgroup app && adduser -r -g app app
USER app
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD [ "python", "app.py" ]