import mysql.connector

def backup_mysql_db(host, user, password, database, backup_file):
    try:
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cursor = conn.cursor()

        cursor.execute(f"SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]

        with open(backup_file, "w") as f:
            for table in tables:
                # Get CREATE TABLE statement
                cursor.execute(f"SHOW CREATE TABLE {table}")
                create_table_stmt = cursor.fetchone()[1]
                f.write(f"{create_table_stmt};\n\n")

                # Get table data
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                for row in rows:
                    values = ', '.join(f"'{str(value)}'" if isinstance(value, str) else str(value) for value in row)
                    f.write(f"INSERT INTO {table} VALUES ({values});\n")
                f.write("\n")

        print(f"Backup successful: {backup_file}")
    except Exception as e:
        print(f"Backup failed: {e}")
    finally:
        cursor.close()
        conn.close()

# Example Usage
backup_mysql_db("localhost", "root", "", "sasi_kannan", "backups/sasi_kannan_backup.sql")
