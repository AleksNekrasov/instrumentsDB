# 🛠️ Инвентаризация инструментов — FastAPI + PostgreSQL

Полноценный backend-проект для учета инструментов, сотрудников, выдачи/возврата оборудования и работы с базой данных.

## 📌 Технологии проекта

- **FastAPI** — backend API
- **PostgreSQL** — база данных
- **SQLAlchemy (Async)** — ORM
- **Alembic** — миграции базы данных
- **Pydantic** — валидация данных
- **Python 3.11+**

---
# 📥 Как установить проект себе на компьютер (Пошагово для новичка)
---

# ШАГ 1. Установить необходимые программы

## Установить Python
Проверь установлен ли Python:
```bash
python3 --version

Установить Git

```bash
sudo apt install git -y

git --version

Установить PostgreSQL
sudo apt install postgresql postgresql-contrib -y

psql --version

-- ** ШАГ 2. Скачать проект из GitHub **

Открой терминал и перейди в папку, где будут проекты:
к примеру:
cd ~/Documents

Скачать репозиторий:
https://github.com/AleksNekrasov/instrumentsDB.git

ШАГ 3. Открыть проект в PyCharm
Запусти PyCharm
Нажми Open
Выбери папку проекта
Нажми Open as Project

ШАГ 4. Создать виртуальное окружение Python

В терминале проекта:
python3 -m venv venv

Активировать:
source venv/bin/activate

ШАГ 5. Установить зависимости проекта
pip install -r requirements.txt

Если ошибка pip старая:
pip install --upgrade pip
pip install -r requirements.txt

ШАГ 6. Настроить PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

Проверить:
sudo systemctl status postgresql

Зайти в PostgreSQL
sudo -u postgres psql

Создать пользователя БД
CREATE DATABASE tools_db OWNER tool_user;

Выдать права
GRANT ALL PRIVILEGES ON DATABASE tools_db TO tool_user;

Выйти
\q

ШАГ 7. Создать файл .env
В корне проекта создай файл .env:

Вставь в него эту строку:
DATABASE_URL=postgresql+asyncpg://tool_user:123456@localhost/tools_db

📌 Что означает строка подключения
postgresql+asyncpg://ЛОГИН:ПАРОЛЬ@ХОСТ/БАЗА

ШАГ 8. Выполнить миграции Alembic
В Терминале:
alembic upgrade head
Это создаст таблицы в PostgreSQL.

ШАГ 9.Как Запустить проект:
В Терминале:
uvicorn app.main:app --reload

ШАГ 10. Открыть браузер
После запуска:
http://127.0.0.1:8000

Swagger документация:
http://127.0.0.1:8000/docs



🔄 Каждый следующий запуск проекта
cd project_folder   # заходим в проект 
source venv/bin/activate
uvicorn app.main:app --reload


❗ Частые ошибки
Ошибка: ModuleNotFoundError
Решение:
pip install -r requirements.txt

Ошибка: connection refused PostgreSQL
Запустить БД:
sudo systemctl start postgresql

Ошибка: password authentication failed
Проверь .env

Ошибка: alembic не найден
pip install alembic

🚀 Если хочешь развернуть проект заново полностью
git clone ...
cd ...
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
создать .env
создать БД
alembic upgrade head
uvicorn app.main:app --reload


👨‍💻 Автор проекта
Backend система учета инструментов на FastAPI.
Некрасов Александр.
nsk540010@gmail.com





























