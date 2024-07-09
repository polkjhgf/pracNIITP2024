import psycopg2
from config import host, user, password, db_name


def create_database() :
    connection = None
    try :
        # Connect to PostgreSQL server
        connection = psycopg2.connect (
            host=host,
            user=user,
            password=password
        )
        connection.autocommit = True
        cursor = connection.cursor ()

        # Create database
        cursor.execute ( f"CREATE DATABASE {db_name}" )
        print ( f"Database {db_name} created successfully" )

        cursor.close ()
        connection.close ()

        # Connect to the newly created database
        connection = psycopg2.connect (
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cursor = connection.cursor ()

        # Create tables
        cursor.execute ( """
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            );
        """ )
        cursor.execute ( """
            CREATE TABLE events (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                event_time TIMESTAMP NOT NULL
            );
        """ )
        cursor.execute ( """
            CREATE TABLE user_events (
                user_id INT REFERENCES users(id) ON DELETE CASCADE,
                event_id INT REFERENCES events(id) ON DELETE CASCADE,
                PRIMARY KEY (user_id, event_id)
            );
        """ )
        connection.commit ()
        print ( "Tables created successfully" )
    except Exception as _ex :
        print ( "[INFO] Error while working with PostgreSQL", _ex )
        if connection :
            connection.rollback ()
    finally :
        if connection :
            cursor.close ()
            connection.close ()


if __name__ == "__main__" :
    create_database ()
