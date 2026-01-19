FROM python:3.11-slim
 
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]
EXPOSE 5000
