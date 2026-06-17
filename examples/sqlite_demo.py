import sqlite3
import json


def main():
    connection = sqlite3.connect("phase1_test.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            embedding TEXT NOT NULL
        )
    """)

    sample_content = "SQLite stores data in a local database file."
    sample_embedding = [0.12, 0.45, -0.33, 0.87]

    cursor.execute(
        "INSERT INTO documents (content, embedding) VALUES (?, ?)",
        (sample_content, json.dumps(sample_embedding))
    )

    connection.commit()

    cursor.execute("SELECT id, content, embedding FROM documents")
    rows = cursor.fetchall()

    for row in rows:
        doc_id = row[0]
        content = row[1]
        embedding = json.loads(row[2])

        print("ID:", doc_id)
        print("Content:", content)
        print("Embedding:", embedding)
        print()

    connection.close()


if __name__ == "__main__":
    main()