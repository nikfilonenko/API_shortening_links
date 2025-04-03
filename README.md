#### Запуск сервиса

```python
docker system prune -af  
docker-compose up --build           
```

- или:

```python
docker run -d -p 5432:5432 -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=shortener postgres:15
docker run -d -p 6379:6379 redis:7
```