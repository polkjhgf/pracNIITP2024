import psycopg2
from config import host, user, password, db_name

def bdConnect():
    try:
        # connect to exist database
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        return connection
    except Exception as _ex:
        print("[INFO] Error while working with PostgreSQL", _ex)
        return None

def get_user_id_by_name(connection, name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE name = %s",
                (name,)
            )
            user_id = cursor.fetchone()
            return user_id[0] if user_id else None
    except Exception as _ex:
        print("[INFO] Error while fetching user ID", _ex)
        return None

def create_user(connection, name):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (name) VALUES (%s) RETURNING id",
                (name,)
            )
            connection.commit()
            user_id = cursor.fetchone()[0]
            print(f"User {name} created with ID {user_id}")
            return user_id
    except Exception as _ex:
        print("[INFO] Error while creating user", _ex)
        return None

def show_events_for_user(connection, user_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    e.id AS event_id,
                    e.name AS event_name,
                    e.description AS event_description,
                    e.event_time AS event_time
                FROM
                    events e
                JOIN
                    user_events ue ON e.id = ue.event_id
                WHERE
                    ue.user_id = %s;
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"Event ID: {row[0]}, Event Name: {row[1]}, Description: {row[2]}, Time: {row[3]}")
            else:
                print("User is not signed up for any events.")
    except Exception as _ex:
        print("[INFO] Error while fetching user events", _ex)

def show_all_events(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, description, event_time FROM events"
            )
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"Event ID: {row[0]}, Event Name: {row[1]}, Description: {row[2]}, Time: {row[3]}")
            else:
                print("No events found.")
    except Exception as _ex:
        print("[INFO] Error while fetching events", _ex)

def menu():
    connection = bdConnect()
    if not connection:
        return

    print("Введите имя:", end=" ")
    name = input()

    user_id = get_user_id_by_name(connection, name)
    if not user_id:
        print("User not found. Creating a new user.")
        user_id = create_user(connection, name)
        if not user_id:
            connection.close()
            return

    while True:
        print("Выберите нужный пункт")
        print("1 - Показать мероприятия, на которые вы подписаны")
        print("2 - Показать всевозможные мероприятия")
        print("3 - Создать мероприятие")
        print("4 - Выйти")
        punkt = int(input())
        if punkt == 1:
            show_events_for_user(connection, user_id)
        elif punkt == 2:
            show_all_events(connection)
            print("")
        elif punkt == 3:
            pass  # Здесь можно добавить код для создания нового мероприятия
        elif punkt == 4:
            break
        else:
            print("Неверный пункт меню, попробуйте снова")

    connection.close()
    print("PostgreSQL connection closed")

if __name__ == "__main__":
    menu()
