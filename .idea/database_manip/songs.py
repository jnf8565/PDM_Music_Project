from database_manip.cursor import query
from datetime import *

def search_songs():
    term = input("Enter search term for song, artist, album, or genre: ").strip()
    while not term:
        print("Search term cannot be empty.")
        term = input("Enter search term for song, artist, album, or genre: ").strip()

    sort_by_options = ["song", "artist", "album", "genre", "year", "default"]
    sort_by = input(f"Sort by ({'/'.join(sort_by_options)}), default is 'song': ").strip().lower()
    if sort_by not in sort_by_options:
        print("Invalid sort option, defaulting to 'song'.")
        sort_by = "song"

    order = input("Order ('asc' or 'desc'), default is 'asc': ").strip().lower()
    if order not in ["asc", "desc"]:
        print("Invalid order, defaulting to 'asc'.")
        order = "asc"

    sort_map = {
        "song": "s.Title",
        "artist": "a.Name",
        "album": "al.Title",
        "genre": "g.Name",
        "year": "s.ReleaseDate"
    }
    sort_col = sort_map.get(sort_by, "s.Title")

    # Escape single quotes in term
    safe_term = term.replace("'", "''")
    like_term = f"%{safe_term}%"

    # STEP 1 — Find matching song IDs
    song_ids = query(f"""
        SELECT DISTINCT s.SUID
        FROM Song s
        LEFT JOIN CreatesS cs ON s.SUID = cs.SUID
        LEFT JOIN Artist a ON cs.ARUID = a.ARUID
        LEFT JOIN ContainsAS ca ON s.SUID = ca.SUID
        LEFT JOIN Album al ON ca.ALID = al.ALID
        LEFT JOIN IsASG ig ON s.SUID = ig.SUID
        LEFT JOIN Genre g ON ig.GID = g.GID
        WHERE LOWER(s.Title) LIKE LOWER('{like_term}')
           OR LOWER(a.Name) LIKE LOWER('{like_term}')
           OR LOWER(al.Title) LIKE LOWER('{like_term}')
           OR LOWER(g.Name) LIKE LOWER('{like_term}');
    """, (), True)

    if not song_ids:
        print("No songs found under inputted search term.")
        return []

    # Extract SUIDs and create IN clause
    song_ids_list = [str(row[0]) for row in song_ids]
    placeholders = ",".join(song_ids_list)

    # STEP 2 — Fetch detailed info
    results = query(f"""
        SELECT DISTINCT s.SUID,
               s.Title AS Song,
               a.Name AS Artist,
               al.Title AS Album,
               g.Name AS Genre,
               s.Length,
               s.ReleaseDate,
               COUNT(l.UID) AS ListenCount
        FROM Song s
        JOIN CreatesS cs ON s.SUID = cs.SUID
        JOIN Artist a ON cs.ARUID = a.ARUID
        JOIN ContainsAS ca ON s.SUID = ca.SUID
        JOIN Album al ON ca.ALID = al.ALID
        LEFT JOIN ListensTo l ON s.SUID = l.SUID
        LEFT JOIN IsASG ig ON s.SUID = ig.SUID
        LEFT JOIN Genre g ON ig.GID = g.GID
        WHERE s.SUID IN ({placeholders})
        GROUP BY s.SUID, s.Title, a.Name, al.Title, g.Name, s.Length, s.ReleaseDate
        ORDER BY {sort_col} {order.upper()}, a.Name {order.upper()};
    """, (), True)

    if not results:
        print("No detailed song info found.")
        return []

    print(f"\nSearch results for '{term}':\n")
    for result in results:
        print("ID: " + str(result[0]) + ", Song Name: \"" + str(result[1]) + "\", Artist: " + str(result[2]) +", Album Name: \"" + result[3] + "\"")



def get_song_id(song_identifier):
    if isinstance(song_identifier, int) or song_identifier.isdigit():
        return int(song_identifier)
    
    result = (f"""SELECT SUID FROM Song 
              WHERE LOWER(Title) LIKE LOWER('%{song_identifier}%') LIMIT 1;
              """, (), True)
    return result[0][0] if result else None


def song_played(uid, song_identifier):
    songs = query(f"""
        SELECT s.suid, s.title, a.name AS artist, al.title AS album
        FROM song s
        JOIN createss cs ON s.suid = cs.suid
        JOIN artist a ON cs.aruid = a.aruid
        LEFT JOIN containsas ca ON s.suid = ca.suid
        LEFT JOIN album al ON ca.alid = al.alid
        WHERE LOWER(s.title) LIKE LOWER('%{song_identifier}%')
        ORDER BY s.title ASC;
    """, (), fetch=True)

    if not songs:
        print(f"No songs found matching '{song_identifier}'.")
        return False

    if len(songs) > 1:
        print(f"\nMultiple songs found for '{song_identifier}':")
        for i, (suid, title, artist, album) in enumerate(songs, start=1):
            album_display = album if album else "No Album"
            print(f"{i}. {title} — {artist} ({album_display})")

        try:
            choice = int(input("Enter the number of the song to play: ").strip())
            if not (1 <= choice <= len(songs)):
                print("Invalid selection.")
                return False
        except ValueError:
            print("Please enter a valid number.")
            return False

        suid, title, artist, album = songs[choice - 1]
    else:
        suid, title, artist, album = songs[0]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = query(f"""
        INSERT INTO ListensTo (suid, uid, starttime)
        VALUES ({suid}, {uid}, '{now}') RETURNING starttime;
        """, (), True)

    if result:
        print(f"Recorded play of '{title}' by {artist}.")
        return True
    else:
        print("Error recording song play.")
        return False


def rate_song(uid, song_identifier):
    songs = query(f"""
        SELECT s.suid, s.title, a.name AS artist, al.title AS album
        FROM song s
        JOIN createss cs ON s.suid = cs.suid
        JOIN artist a ON cs.aruid = a.aruid
        LEFT JOIN containsas ca ON s.suid = ca.suid
        LEFT JOIN album al ON ca.alid = al.alid
        WHERE LOWER(s.title) LIKE LOWER('%{song_identifier}%')
        ORDER BY s.title ASC;
    """, (), fetch=True)

    if not songs:
        print(f"No songs found matching '{song_identifier}'.")
        return False
    if len(songs) > 1:
        print(f"\nMultiple songs found for '{song_identifier}':")
        for i, (suid, title, artist, album) in enumerate(songs, start=1):
            album_display = album if album else "No Album"
            print(f"{i}. {title} — {artist} ({album_display})")

        try:
            selection = int(input("Enter the number of the song to rate: ").strip())
            if not (1 <= selection <= len(songs)):
                print("Invalid selection.")
                return False
        except ValueError:
            print("Please enter a valid number.")
            return False
        suid, title, artist, album = songs[selection - 1]

    else:
        suid, title, artist, album = songs[0]
    try:
        stars = int(input(f"Enter your rating for '{title}' by {artist} (1–5): ").strip())
        if stars < 1 or stars > 5:
            print("Error: Rating must be between 1 and 5.")
            return False
    except ValueError:
        print("Error: Please enter a valid number between 1 and 5.")
        return False
    check_sql = f"SELECT stars FROM rates WHERE suid = {suid} AND uid = {uid};"
    existing = query(check_sql, (), fetch=True)
    if existing:
        query(f"UPDATE rates SET stars = {stars} WHERE suid = {suid} AND uid = {uid};")
        print(f"Updated rating for '{title}' by {artist} to {stars} stars.")
    else:
        query(f"INSERT INTO rates (suid, uid, stars) VALUES ({suid}, {uid}, {stars});")
        print(f"Rated '{title}' by {artist} {stars} stars.")
    return True

def top_songs_last_30():
    results = query("""
        SELECT s.Title, a.Name, COUNT(l.SUID) AS plays
        FROM ListensTo l
        JOIN song s ON s.SUID = l.SUID
        JOIN CreatesS cs ON cs.SUID = l.SUID
        JOIN Artist a ON cs.ARUID = a.ARUID
        WHERE l.StartTime >= NOW() - INTERVAL '30 Days'
        GROUP BY s.SUID, s.Title, a.Name
        ORDER BY plays DESC
        LIMIT 50;""", fetch=True)
    if not results:
        print("No listening data available")
        return
    print("Top 50 songs in the last 30 days:")
    for i, (title, artist, plays) in enumerate(results, 1):
        print(f"{i}. {title} — {artist} ({plays} plays)")

def top_songs_followed(uid):
    results = query(f"""
        SELECT s.Title, a.Name, COUNT(l.SUID) AS plays
        FROM ListensTo l
        JOIN song s ON s.SUID = l.SUID
        JOIN CreatesS cs ON cs.SUID = l.SUID
        JOIN Artist a ON cs.ARUID = a.ARUID
        WHERE l.UID IN ( 
            SELECT followed FROM follows WHERE follower = {uid}
        )
        GROUP BY s.SUID, s.Title, a.Name
        ORDER BY plays DESC
        LIMIT 50;""", fetch=True)
    if not results:
        print("No listening data available")
        return
    print("Top 50 songs from users you follow")
    for i, (title, artist, plays) in enumerate(results, 1):
        print(f"{i}. {title} — {artist} ({plays} plays)")

def top_genres():
    results = query("""
        SELECT g.Name, COUNT(*) AS plays
        FROM ListensTo l
        JOIN IsASG ig on l.SUID = ig.SUID
        JOIN Genre g on g.GID = ig.GID
        WHERE l.StartTime >= DATE_TRUNC('month', NOW())
        GROUP BY g.Name
        ORDER BY plays DESC
        LIMIT 5;""", fetch=True)
    if not results:
        print("No listening data available")
        return
    print("Top 5 genres this month")
    for i, (genre, plays) in enumerate(results, 1):
        print(f"{i}. {genre} ({plays} plays)")

def recommend_songs(uid):
    user_top_genre = query("""
        SELECT g.GID, g.NAME, COUNT(*) AS plays
        FROM ListensTo l
        JOIN IsASG ig ON l.SUID = ig.SUID
        JOIN GENRE g ON g.GID = ig.GID
        WHERE l.uid = %s
        GROUP BY g.GID, g.NAME
        ORDER BY plays DESC
        LIMIT 2;
        """, (uid,), fetch=True)
    
    if not user_top_genre:
        print("No listening data found.")
        return
    
    top_songs_str = """
        WITH topSongs AS (
            SELECT l.suid,
                    COUNT(*) AS listens,
                    ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS row
                FROM listensto l
                JOIN IsASG ig ON l.SUID = ig.SUID
                WHERE ig.GID = %s
                GROUP BY l.SUID
        )
        SELECT ts.SUID, s.TITLE, s.ARTIST, ts.LISTENS
        FROM topSongs ts
        JOIN song s ON s.SUID = ts.SUID
        WHERE ts.row <= 5;
        """
    
    genre_id1 = user_top_genre[0][0]
    genre_name1 = user_top_genre[0][1]
    genre_songs1 = query(top_songs_str, (genre_id1,), fetch=True)

    print(f"\nTop recommendations from {genre_name1}:\n")
    for song in genre_songs1:
        print(song)

    if not user_top_genre[1][0]:
        print("Only one genre on record.")
    else:
        genre_id2 = user_top_genre[1][0]
        genre_name2 = user_top_genre[1][1]
        genre_songs2 = query(top_songs_str, (genre_id2,), fetch=True)
        print(f"\nTop recommendations from {genre_name2}:\n")
        for song in genre_songs2:
            print(f"Title: {song[1]}, Artist: {song[2]}")

    top_from_followed = query("""
        WITH followed AS (
            SELECT followed AS UID
            FROM follows
            WHERE follower = %s
        ),
        popularity AS (
            SELECT l.SUID, COUNT(*) AS listens,
                ROW_NUMBER() OVER (ORDER BY COUNT(*) DESC) AS row
            FROM listensto l
            JOIN followed f ON l.UID = f.UID
            JOIN IsASG ig ON l.SUID = ig.SUID
            WHERE ig.GID IN (%s, %s)
            GROUP BY l.SUID
        )
        SELECT p.SUID, s.TITLE, s.ARTIST, p.LISTENS
        FROM popularity p
        JOIN song s ON s.SUID = p.SUID
        WHERE row <= 5;
        """, (uid, genre_id1, genre_id2), fetch=True)
    
    print("\nTop songs among followed users:\n")
    if not top_from_followed:
        print("No data found")
    else:
        for song in top_from_followed:
            print(song)
    
    