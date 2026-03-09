import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'database': 'back2me_db'
}

def update_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Drop the old messages table
        cursor.execute("DROP TABLE IF EXISTS messages")
        print("Dropped 'messages' table.")
        
        # Create the new comments table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            comment_text TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        print("Created 'comments' table.")
        
        conn.commit()
        cursor.close()
        conn.close()
    except pymysql.Error as e:
        print(f"Error updating MySQL: {e}")

if __name__ == "__main__":
    update_db()
