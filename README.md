# Backend

## Стэк:
    FastAPI + MongoDB + Redis
## Как развернуть:
###   из докера весь сервис:
1. Клонируем
```bash
foo@bar:~$ git clone https://github.com/ProgramEngineeringOurJira/Backend
```
2. Заходим в папку
```bash
foo@bar:~$ cd Backend
```
3. Настройте файл .env для запуска
```bash
    foo@bar:~$ vim .env
    REDIS_URL=redis://localhost:6379
    MONGO_URL=mongodb://localhost:27017
    MG_PASS=aboba
    MG_USER=aboba
    JWT_SECRET=mysecret
    JWT_ALG=HS256
    ALGORITHM=HS256
    AUTH_SECRET=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
    EMAIL_HOST=""
    EMAIL_PORT=
    EMAIL_USERNAME=""
    EMAIL_PASSWORD=""
    EMAIL_FROM=""
    LOGIN_URL="/login"
    WORKPLACE_URL="/workplaces"
    AVATAR_SIZE=60
    BACKGROUND_COLOR="#f2f1f2"
```
4. Запускаем докер
```bash
foo@bar:~$ docker-compose up
```
#### Swagger доступен по /swagger
Или доступен по [ссылке](http://81.200.149.209:8080/swagger) онлайн


