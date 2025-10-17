import json
import pyodbc

def load_content_json(json_file_path, **conn_config):
    """
    Load content.json file into bronze.content table
    """
    print("=== DEBUG CONNECTION CONFIG ===")
    print(conn_config)
    print("=== END DEBUG ===")
    
    # Read JSON file
    print(f"Reading JSON file: {json_file_path}")
    with open(json_file_path, 'r') as f:
        data = json.load(f)
    
    print(f"Found {len(data['movies'])} movies and {len(data['series'])} series")
    
    # Connect to database
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={conn_config['server']};"
        f"DATABASE={conn_config['database']};"
        f"UID={conn_config['username']};"
        f"PWD={conn_config['password']}"
    )
    cursor = conn.cursor()
    
    try:
        # Create bronze.content table if it doesn't exist
        create_table_sql = """
        IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'bronze' AND TABLE_NAME = 'content')
        BEGIN
            CREATE TABLE bronze.content (
                content_id NVARCHAR(50) PRIMARY KEY,
                title NVARCHAR(255),
                genre NVARCHAR(500),
                duration_minutes INT,
                release_year INT,
                rating FLOAT,
                views_count INT,
                production_budget BIGINT,
                content_type NVARCHAR(50),  -- 'movie' or 'series'
                seasons INT NULL,           -- for series only
                total_episodes INT NULL     -- for series only
            )
        END
        """
        print("Creating bronze.content table if it doesn't exist...")
        cursor.execute(create_table_sql)
        conn.commit()
        
        # Clear existing data
        print("Clearing existing data...")
        cursor.execute("DELETE FROM bronze.content")
        conn.commit()
        
        # Insert movies
        print("Inserting movies...")
        movie_count = 0
        for movie in data['movies']:
            # Convert genre array to comma-separated string
            genre_str = ', '.join(movie['genre']) if isinstance(movie['genre'], list) else str(movie['genre'])
            
            insert_sql = """
            INSERT INTO bronze.content 
            (content_id, title, genre, duration_minutes, release_year, rating, views_count, production_budget, content_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'movie')
            """
            
            cursor.execute(insert_sql, (
                movie['content_id'],
                movie['title'],
                genre_str,
                movie['duration_minutes'],
                movie['release_year'],
                movie['rating'],
                movie['views_count'],
                movie['production_budget']
            ))
            movie_count += 1
        
        print(f"Inserted {movie_count} movies")
        
        # Insert series
        print("Inserting series...")
        series_count = 0
        for series in data['series']:
            # Convert genre array to comma-separated string
            genre_str = ', '.join(series['genre']) if isinstance(series['genre'], list) else str(series['genre'])
            
            # Calculate total episodes
            total_episodes = sum(series['episodes_per_season'])
            
            # Calculate total duration in minutes (avg_episode_duration * total_episodes)
            duration_minutes = series['avg_episode_duration'] * total_episodes
            
            insert_sql = """
            INSERT INTO bronze.content 
            (content_id, title, genre, duration_minutes, release_year, rating, views_count, production_budget, content_type, seasons, total_episodes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'series', ?, ?)
            """
            
            # Note: series don't have release_year, using 2020 as default or you could calculate from other data
            release_year = 2020  # You might want to add release_year to series data or calculate it
            
            cursor.execute(insert_sql, (
                series['content_id'],
                series['title'],
                genre_str,
                duration_minutes,
                release_year,
                series['rating'],
                series['total_views'],  # Note: series uses 'total_views' instead of 'views_count'
                series['production_budget'],
                series['seasons'],
                total_episodes
            ))
            series_count += 1
            
        print(f"Inserted {series_count} series")
        
        # Commit all changes
        conn.commit()
        print("All data committed successfully!")
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM bronze.content WHERE content_type = 'movie'")
        movie_total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM bronze.content WHERE content_type = 'series'")
        series_total = cursor.fetchone()[0]
        
        print(f"=== LOAD SUMMARY ===")
        print(f"Movies loaded: {movie_total}")
        print(f"Series loaded: {series_total}")
        print(f"Total content items: {movie_total + series_total}")
        print(f"====================")
        
    except Exception as e:
        print(f"Error loading JSON: {str(e)}")
        conn.rollback()
        raise
        
    finally:
        cursor.close()
        conn.close()