from cursor import query
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
    """, fetch=True)

    if not results:
        print("No songs found under inputted search term")
        return []
    print(f"Search results for '{term}':\n")
    print(results)


# def song_played(uid, sid):


# def rate_song(uid, suid, stars):
