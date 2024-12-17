# CloudComputing - TAM Book

This application is designed to streamline the operations of an online bookstore. It simplifies the management of customers, books data and reviews and also facilitates placing orders.

### DB Diagram

![Clouddiagramaconceptuala drawio](https://github.com/user-attachments/assets/8f786f92-d1f0-4629-83ed-742b1b874bdb)

### Micro-services:

1.	Auth Service – login & register
2.	Book Service
3.	Order Service (user orders, place new order, order status)
4.	Payment Service 
5.	Review & Ratings Service
6.	Analytics Service – Prometheus
7.	Notification Service


### Dev commands

 * **Create microservice**:
    ```
    name-microservices:
    build:
      context: ./NameMicroservices
      dockerfile: Dockerfile
    container_name: tam-book-app
    networks:
      - my-network
    ports:
      - "5004:8000"
    environment:
      DB_HOST: postgres
      DB_NAME: db
      DB_USERNAME: postgres
      DB_PASSWORD: my-secret-pw```

* **Start microservice**:  ``` docker-compose up --build ```
