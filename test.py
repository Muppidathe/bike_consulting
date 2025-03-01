import mysql.connector

print("Starting MySQL connection...")

try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        port=3306,
        password="",
        database="kannan",
        connect_timeout=5  # Force timeout if it hangs
    )
    print("✅ Connection Successful!")
except mysql.connector.Error as e:
    print("❌ Connection Failed:", e)

print("End of script")
