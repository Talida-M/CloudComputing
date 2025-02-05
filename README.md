# CloudComputing - TAM Book

This application is designed to streamline the operations of an online bookstore. It simplifies the management of customers, books data and reviews and also facilitates placing orders. 
It has:
- 4 microservices with their own database 
- docker-compose
- docker-swarm with one manager node and one worker (2 virtual machines)
- user interface that connects the url for interface with API from microservices

### DBs Diagrams for each microservice

![Diagrame baze de date per microservicii](https://github.com/user-attachments/assets/66690a57-35fb-4c47-b697-9828e3432818)

### Microservices:
![microservices](https://github.com/user-attachments/assets/4fa50d73-97b1-48e9-afb1-588c5921c803)

1.	User Microservice – login & register
2.	Book Microservice - book and author management
3.	Order Microservice 

  	a. OrderApi
  	 
- add books to order,
- increase/decrease/remove book from order,
- list all orders
- sent order - with RabbitMQ (change the order status to success)
  
    b. Consumer
  
- where the status is changed with RabbitMQ help
4.	Review Microservice - add review

The application has a user interface: UserInterface 

### Implemented bonuses

The application has implemented 2 bonuses:
1.	Metrics – Prometheus
2.	Logging with syslog-ng

### Example of microservices from docker-compose good in docker-swarm

![docker_compose_from_swarm](https://github.com/user-attachments/assets/381171c3-b2b8-41ab-9c98-ffd3ae876763)

### Docker-compose file modified for docker-swarm
[Docker-compose](https://github.com/Talida-M/CloudComputing/blob/68bb624e504ed54680f458d7bd98488944d13596/docker_compose_yml_from_Swarm.txt)

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
