import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123'
}

def init_db():
    try:
        # Connect to MySQL server without selecting a DB
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS back2me_db")
        print("Database 'back2me_db' created or already exists.")
        
        # Select database
        cursor.execute("USE back2me_db")
        
        # Create Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Create Posts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            item_name VARCHAR(255) NOT NULL,
            post_type ENUM('lost', 'found') NOT NULL,
            description TEXT,
            location VARCHAR(255),
            image_url VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # Create Messages table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            message_text TEXT NOT NULL,
            read_status BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        print("Tables created successfully.")
        
        conn.commit()
        cursor.close()
        conn.close()
    except pymysql.Error as e:
        print(f"Error connecting to MySQL: {e}")

if __name__ == "__main__":
    init_db()
