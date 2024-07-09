import psycopg2
from config import host, user, password, db_name

def bdConnect():
    try:
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
            print(f"{name} ваш id {user_id}")
            return user_id
    except Exception as _ex:
        print("[INFO] Error while creating user", _ex)
        connection.rollback()
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
                    print(f"ID {row[0]}, имя {row[1]}, описание {row[2]}, время {row[3]}")
            else:
                print("Вы не подписались ни на одно мероприятие")
    except Exception as _ex:
        print("[INFO] Error while fetching user events", _ex)

def show_all_events_not_signed_by_user(connection, user_id):
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
                LEFT JOIN
                    user_events ue ON e.id = ue.event_id AND ue.user_id = %s
                WHERE
                    ue.user_id IS NULL;
                """,
                (user_id,)
            )
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"id {row[0]}, имя: {row[1]}, описание {row[2]}, время {row[3]}")
            else:
                print("Мероприятие не найдено")
    except Exception as _ex:
        print("[INFO] Error while fetching events not signed by user", _ex)

def subscribe_user_to_event(connection, user_id, event_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO user_events (user_id, event_id) VALUES (%s, %s)",
                (user_id, event_id)
            )
            connection.commit()
            print(f"{user_id} подписался на мероприятие {event_id}")
    except Exception as _ex:
        print("[INFO] Error while subscribing to event", _ex)
        connection.rollback()

def unsubscribe_user_from_event(connection, user_id, event_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM user_events WHERE user_id = %s AND event_id = %s",
                (user_id, event_id)
            )
            connection.commit()
            print(f"{user_id} отписал от мероприятия {event_id}")
    except Exception as _ex:
        print("[INFO] Error while unsubscribing from event", _ex)
        connection.rollback()

def show_all_events(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, description, event_time FROM events"
            )
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"id {row[0]}, имя {row[1]}, описание {row[2]}, время {row[3]}")
            else:
                print("Новых мероприятий не найдено")
    except Exception as _ex:
        print("[INFO] Error while fetching events", _ex)

def create_event(connection, name, description, event_time):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO events (name, description, event_time) VALUES (%s, %s, %s) RETURNING id",
                (name, description, event_time)
            )
            connection.commit()
            event_id = cursor.fetchone()[0]
            print(f"Мероприятие '{name}' был создан с id '{event_id}'")
            return event_id
    except Exception as _ex:
        print("[INFO] Error while creating event", _ex)
        connection.rollback()
        return None

def menu():
    connection = bdConnect()
    if not connection:
        return

    print("Введите имя:", end=" ")
    name = input()

    user_id = get_user_id_by_name(connection, name)
    if not user_id:
        print("Имя не найдено. создание нового юзера")
        user_id = create_user(connection, name)
        if not user_id:
            connection.close()
            return

    while True:
        print("Выберите нужный пункт")
        print("1 - Показать мероприятия, на которые вы подписаны")
        print("2 - Показать мероприятия, на которые вы не подписаны")
        print("3 - Создать мероприятие")
        print("4 - Выйти")
        punkt = int(input())
        if punkt == 1:
            show_events_for_user(connection, user_id)
            print("Введите ID мероприятия, от которого хотите отписаться:", end=" ")
            event_id = int(input())
            unsubscribe_user_from_event(connection, user_id, event_id)
        elif punkt == 2:
            show_all_events_not_signed_by_user(connection, user_id)
            print("Введите ID мероприятия, на которое хотите подписаться:", end=" ")
            event_id = int(input())
            subscribe_user_to_event(connection, user_id, event_id)
        elif punkt == 3:
            print("Введите название мероприятия:", end=" ")
            event_name = input()
            print("Введите описание мероприятия:", end=" ")
            event_description = input()
            print("Введите время мероприятия (YYYY-MM-DD HH:MM:SS):", end=" ")
            event_time = input()
            create_event(connection, event_name, event_description, event_time)
        elif punkt == 4:
            break
        else:
            print("Неверный пункт меню, попробуйте снова")

    connection.close()
    print("PostgreSQL connection closed")

if __name__ == "__main__":
    menu()
