from database_manip.cursor import query
from database_manip.playlists import find_song, select_song
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

    if sort_by == "default":
        order_clause = "s.Title ASC, a.Name ASC"
    else:
        sort_map = {
            "song": "s.Title",
            "artist": "a.Name",
            "genre": "g.Name",
            "year": "s.ReleaseDate"
        }
        sort_col = sort_map.get(sort_by.lower(), "s.Title")
        order_clause = f"{sort_col} {order.upper()}, a.Name {order.upper()}"     
    results = query(f"""
        SELECT s.SUID,
               s.Title AS Song,
               a.Name  AS Artist,
               al.Title AS Album,
               s.Length,
               COUNT(l.UID) AS ListenCount
        FROM Song s
        JOIN CreatesS cs ON s.SUID = cs.SUID
        JOIN Artist a ON cs.ARUID = a.ARUID
        JOIN ContainsAS ca ON s.SUID = ca.SUID
        JOIN Album al ON ca.ALID = al.ALID
        LEFT JOIN ListensTo l ON s.SUID = l.SUID
        LEFT JOIN IsASG ig ON s.SUID = ig.SUID
        LEFT JOIN Genre g ON ig.GID = g.GID
        WHERE LOWER(s.Title) LIKE LOWER('%{term}%')
           OR LOWER(a.Name)  LIKE LOWER('%{term}%')
           OR LOWER(al.Title) LIKE LOWER('%{term}%')
           OR LOWER(g.Name)  LIKE LOWER('%{term}%')
        GROUP BY s.SUID, s.Title, a.Name, al.Title, s.Length, s.ReleaseDate, g.Name
        ORDER BY {order_clause};
    """, True)

    if not results:
        print("No songs found under inputted search term")
        return []
    print(f"Search results for '{term}':\n")
    print(results)

def get_song_id(song_identifier):
    if isinstance(song_identifier, int) or song_identifier.isdigit():
        return int(song_identifier)
    
    result = (f"""SELECT SUID FROM Song 
              WHERE LOWER(Title) LIKE LOWER('%{song_identifier}%') LIMIT 1;
              """, True)
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
    """, fetch=True)

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
    sql = f"""
        INSERT INTO ListensTo (suid, uid, starttime)
        VALUES ({suid}, {uid}, '{now}') RETURNING starttime;
    """
    result = query(sql, fetch=True)

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
    """, fetch=True)

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
    existing = query(check_sql, fetch=True)
    if existing:
        sql = f"UPDATE rates SET stars = {stars} WHERE suid = {suid} AND uid = {uid};"
        query(sql)
        print(f"Updated rating for '{title}' by {artist} to {stars} stars.")
    else:
        sql = f"INSERT INTO rates (suid, uid, stars) VALUES ({suid}, {uid}, {stars});"
        query(sql)
        print(f"Rated '{title}' by {artist} {stars} stars.")

    return True
