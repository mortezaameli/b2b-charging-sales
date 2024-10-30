# B2B seller mobile chrage  

# Start project in develop mode
```sh
docker-compose -f docker-compose.develop.yml build
docker-compose -f docker-compose.develop.yml up
```

---

# Start project in testing mode

```sh
docker-compose -f docker-compose.testing.yml build
docker-compose -f docker-compose.testing.yml up
```

## Unit Testing
```sh
docker-compose -f docker-compose.testing.yml exec web python manage.py test
```

## Load Testing with Locust

* For example, with the following command, the project will be loaded for 30 seconds by 8 users:

  ```sh
  docker-compose -f docker-compose.testing.yml exec web locust -f locustfile.py --headless --users 8 --spawn-rate 2 --run-time 30s --host http://localhost:8000
  ```

* Check DB Consistency after loads:
  ```sh
  curl --location 'http://localhost:8000/billing/check-db-consistency/'
  ```
