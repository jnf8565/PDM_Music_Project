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
    """)

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
    """, True)

    if not results:
        print("No detailed song info found.")
        return []

    print(f"\nSearch results for '{term}':\n")
    for result in results:
        print("ID: " + str(result[0]) + ", Song Name: \"" + str(result[1]) + "\", Artist: " + str(result[2]) +", Album Name: \"" + result[3] + "\"")



def get_song_id(song_identifier):
    if isinstance(song_identifier, int) or song_identifier.isdigit():
        return int(song_identifier)
    
    sql = f"SELECT SUID FROM Song WHERE LOWER(Title) LIKE LOWER('%{song_identifier}%') LIMIT 1;"
    result = query(sql, fetch=True)
    return result[0][0] if result else None


def song_played(uid, song_identifier):
    suid = get_song_id(song_identifier)
    if not suid:
        print("Error: Song not found.")
        return False

    now = datetime.now()
    sql = f"""
        INSERT INTO ListensTo (SUID, UID, StartTime)
        VALUES ({suid}, {uid}, '{now}') RETURNING starttime;
    """
    result = query(sql, True)
    if result and len(result) > 0:
        starttime = result[0][0]

    if abs((starttime - now).total_seconds()) < 1:
        print(f"Recorded play of song '{song_identifier}'.")
        return True
    else:
        print("Error recording song play.")
        return False


def rate_song(uid, song_identifier, stars):
    if stars < 1 or stars > 5:
        print("Error: Rating must be between 1 and 5.")
        return False

    suid = get_song_id(song_identifier)
    if not suid:
        print("Error: Song not found.")
        return False
    try: 
        check_sql = f"SELECT * FROM Rates WHERE SUID = {suid}  AND UID ={uid};"
        existing = query(check_sql, fetch=True)
        if existing:
            sql = f"UPDATE Rates SET Stars = {stars} WHERE SUID = {suid} AND UID = {uid};"
            query(sql)
            print(f"Updated rating for '{song_identifier}' to {stars} stars.")
            return True
        else:
            sql = f"INSERT INTO Rates (SUID, UID, Stars) VALUES ({suid},{uid},{stars});"
            query(sql)
            print(f"Rated '{song_identifier}' {stars} stars.")
            return True
    except Exception:
        print("Error rating song.")
        return False