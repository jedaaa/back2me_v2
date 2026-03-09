import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'mysql123',
    'database': 'back2me_db'
}

def update_posts_table():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Add the 'status' column if it doesn't exist
        try:
            cursor.execute("ALTER TABLE posts ADD COLUMN status ENUM('active', 'resolved') DEFAULT 'active'")
            print("Added 'status' column to 'posts' table.")
        except pymysql.err.OperationalError as e:
            if e.args[0] == 1060: # Duplicate column name
                print("'status' column already exists in 'posts' table.")
            else:
                raise e
        
        conn.commit()
        cursor.close()
        conn.close()
    except pymysql.Error as e:
        print(f"Error updating MySQL: {e}")

if __name__ == "__main__":
    update_posts_table()
