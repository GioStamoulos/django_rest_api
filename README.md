# Article Django REST API 

This Django REST API server provides endpoints for managing articles, authors, tags, and comments.

## Setup

1. **Clone the Repository:**

   ```bash
   git clone <repository_url> && cd django_rest_api

2. **Install Docker:**
    [Docker Documentation](https://docs.docker.com/desktop/)

3. **Build - Run App:**
    ```bash
        docker-compose up -d --build

    * If  POPULATE_DB, RUN_TESTS, MIGRATE_DB enviroment variables are set to true \then db population, tests and migration scripts will be triggered. 

## Consume
### Using cURL
1. **User Authentication:** To authenticate a user and obtain an access token, send a POST request to the /api/token/ endpoint with the user's credentials:

   ```bash
   curl -X POST -d "username=<username>&password=<password>" http://127.0.0.1:8000/api/token/

This will return an access token.

2. **Accessing Endpoints:** With the access token obtained from the authentication step, you can access protected endpoints by including the token in the request headers.

   ```bash
       curl -X GET -H "Authorization: Bearer <access_token>" http://127.0.0.1:8000/api/articles/

    Replace <access_token> with the token obtained from the authentication step.You can use similar cURL commands to perform GET, POST, PUT, PATCH, and DELETE operations on various endpoints such as /articles/, /authors/, /tags/, and
    /comments/.

**PATCH Article**
    ```bash
        curl -X PATCH -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" -d '{"title": "Updated Title"}' http://127.0.0.1:8000/articles/<article_id>/
**PUT Author**
    ```bash
        curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" -d '{"name": "New Name", "email": "new@example.com"}' http://127.0.0.1:8000/authors/<author_id>/
**DELETE Tag**
    ```bash
        curl -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer <access_token>" -d '{"name": "New Name", "email": "new@example.com"}' http://127.0.0.1:8000/authors/<author_id>/

3. **Filtering Endpoints and Pagination:**

    To retrieve a list of articles filtered by year and authors with pagination, you can use:
    ```bash
        curl -X GET -H "Authorization: Bearer <access_token>" "http://127.0.0.1:8000/articles/?year=2022&authors=John%20Doe&page=2"
    Replace <access_token> with the access token obtained from the authentication step.This command will retrieve a list of articles published in the year 2022, authored by John Doe, with pagination applied (default page size of 100 pages).

4.  **Download articles in csv:**

    Users can download articles in CSV format by making a GET request to the /articles//download/ endpoint with optional query parameters for filtering and pagination.Example cURL command:
    ```bash
        curl -H "Authorization: Bearer <access_token>" "http://127.0.0.1:8000/articles//download/?year=2022&authors=John%20Doe"
    This command will download articles published in the year 2022 and authored by John Doe as a CSV file.

5.  **Example**
**-Get Token:**
     ```bash
        $ curl -X POST http://localhost:8000/api/token/ -d "username=george&password=123"
**Output**
    ```bash
        {"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTcxNTI5NDc4OSwiaWF0IjoxNzE1MjA4Mzg5LCJqdGkiOiJkZWRkZWNjZjU3NDI0ZWE5YjdiNTM5MDRjNDc2NGEwZCIsInVzZXJfaWQiOjZ9.AJBH55aG-MjKKMc-2tk_1eN6p0lqDHvyMNszNidtRlk","access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzE1MjA4Njg5LCJpYXQiOjE3MTUyMDgzODksImp0aSI6ImE3NTY3MzlmMTFkODQ1MDI4MDhhNzdlYWRlZTAzZTAyIiwidXNlcl9pZCI6Nn0.5bOv22lm0RwtLHt_TbRmRcAA3BfI82H9MKNh8nQxxF4"}"

**-Get Articles with Pagination (GET Request):**
    ```bash
        $ curl -X GET -H "Authorization: Bearer <access_token>" http://localhost:8000/articles/?page=2
**Output**
    ```bash
    {"count":500,"next":"http://localhost:8000/articles/?page=3","previous":"http://localhost:8000/articles/","results":[{"id":101,"title":"Degree significant popular team somebody her.","abstract":"See artist difficult protect. National item check language wall. Soon half then draw other.","publication_date":"2024-05-02","user":4,"authors":[5],"tags":[1,2,4,5]},{"id":102,"title":"Dream treat fly market voice development investment.","abstract":"Bill stay question must. Help light laugh learn. Him effect black detail recognize effect. Again focus fall break.","publication_date":"2023-09-03","user":6,"authors":[1],"tags":[1,2,4,5]},{"id":103,"title":"Chair pressure owner me.","abstract":"Soldier these nearly include term plan much manager. Central investment approach national.","pu
       ....}