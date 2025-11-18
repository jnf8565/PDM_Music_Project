from database_manip.cursor import query
import psycopg2

def create_playlist(uid):
  try:
      playlist_name = input("Enter playlist name here: ").strip()
      if not playlist_name:
        print("Empty playlist name")
        return
      pid = query("INSERT INTO playlist (name,uid) VALUES (%s, %s) RETURNING pid", (playlist_name, uid), fetch=True)[0][0]
      if pid is not None:
        query("INSERT INTO createsp VALUES (%s, %s)", (uid, pid))
        print(f"Playlist {playlist_name} created")
        return
      else:
        print("PID not found for playlist")
        return None
  except  psycopg2.errors.UniqueViolation as e:
     print("Playlists cannot have duplicate names")
     exit
  except Exception as e:
     print("Database error")
     exit

def get_pid(p_name, uid):
  p_name = p_name.lower().strip()
  result = query("SELECT pid FROM playlist WHERE LOWER(name)=%s AND uid=%s", (p_name, uid), fetch=True)
  if result:
      return result[0][0]
  else:
      return None

def rename_playlist(uid):
  try:
    old_name = input("Enter current name of playlist here: ").lower().strip()
    pid = get_pid(old_name,uid)
    if not pid:
          print(f"Playlist '{old_name}' does not exist")
          return
    new_name = input("Enter new name of playlist here: ").strip()
    if not new_name:
          print("Empty playlist name")
          return
    query("UPDATE playlist SET name=%s WHERE pid=%s", (new_name, pid))
    print(f"Playlist '{old_name}' changed to '{new_name}'")
  except Exception:
     print("Playlist with that name already exists")
  
def find_song(name):
  name = name.strip().replace("'", "''")
  return query("""SELECT suid, title, artist 
               FROM song WHERE title ILIKE %s 
               ORDER BY title ASC""", (f"%{name}%",), fetch=True)

def select_song():
  name_input = input("Enter song name here: ").strip()
  results = find_song(name_input)
  if not results:
      print("No song with that name")
      return 
  if len(results) == 1:
      return results[0][0]
  print("Multiple songs found")
  index = 1
  for song in results:
      song_id = song[0]     # The song's ID
      song_title = song[1]  # The song’s title
      artist = song[2]      # The artist of the song
      print(f"{index}. {song_title} by {artist} (ID: {song_id})")
      index += 1
  selection = input("Enter number for desired song: ")
  try:
      selection = int(selection)
      if 1 <= selection <= len(results):
          return results[selection - 1][0]
      else:
          print("Invalid selection.")
          return None
  except Exception:
      print("Please enter a valid number.")
      return None
    
def slime_playlist(uid):
  name = input("Enter name of playlist to be deleted: ").strip()
  pid = get_pid(name,uid)
  if not pid:
       print(f"Playlist '{name}' does not exist")
       return
  query("DELETE FROM addedsongto WHERE pid=%s", (pid,))
  query("DELETE FROM addedalbumto WHERE pid=%s", (pid,))
  query("DELETE FROM createsp WHERE pid=%s", (pid,))
  query("DELETE FROM playlist WHERE pid=%s", (pid,))
  print("Playlist deleted")

def slime_all_playlists(uid):
  print("Deleting Playlists...")
  playlists = list_user_playlists(uid)

  if not playlists:
     print("No playlists to delete.")
     return
  
  for playlist in playlists:
    pid = playlist[0]
    query("DELETE FROM addedsongto WHERE pid=%s", (pid,))
    query("DELETE FROM addedalbumto WHERE pid=%s", (pid,))
    query("DELETE FROM createsp WHERE pid=%s", (pid,))
    query("DELETE FROM playlist WHERE pid=%s", (pid,))

def add_song_to_playlist(uid):
  p_name = input("Enter name of playlist: ").strip()
  if not p_name:
    print("Empty playlist name")
    return
  pid = get_pid(p_name, uid)
  if not pid:
     print(f"Playlist '{p_name}' does not exist")
  suid = select_song()
  if not suid:
      return
  query("INSERT INTO addedsongto (pid, suid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (pid, suid))
  print("Song added to playlist.")
  
def play_playlist(uid):
  playlists = list_user_playlists(uid)
  if not playlists:
    print("No playlists found")
    return
  selection = input("Enter the number of the playlist to play: ").strip()
  try:
      selection = int(selection)
      if 1 <= selection <= len(playlists):
          pid = playlists[selection - 1][0]
      else:
          print("Invalid selection.")
          return
  except Exception:
      print("Please enter a valid number.")
      return
  songs = query("""
        SELECT s.suid, s.title, s.artist
        FROM addedsongto a
        JOIN song s ON a.suid = s.suid
        WHERE a.pid = %s
        ORDER BY s.title ASC;
    """, (pid,), fetch=True)
  if not songs:
     print("Empty playlist")
     return
  print(f"\nPlaying playlist '{playlists[selection - 1][1]}':")
  for s in songs:
      suid, title, artist = s
      print(f"Now playing: {title} by {artist}")
      query("""
          INSERT INTO listensto (uid, suid, starttime)
          VALUES (%s, %s, NOW())
          ON CONFLICT DO NOTHING;
      """, (uid, suid))
  print("Finished playing playlist.")
   

def remove_song_from_playlist(uid):
    p_name = input("Enter playlist name here: ").strip()
    if not p_name:
        print("Empty playlist name.")
        return

    pid = get_pid(p_name, uid)
    if not pid:
        print(f"Playlist '{p_name}' does not exist.")
        return

    # Step 2: Get all songs currently in the playlist
    songs = query("""
        SELECT s.suid, s.title, a.name AS artist
        FROM addedsongto ad
        JOIN song s ON ad.suid = s.suid
        JOIN createss cs ON s.suid = cs.suid
        JOIN artist a ON cs.aruid = a.aruid
        WHERE ad.pid = %s
        ORDER BY s.title ASC;
    """, (pid,), fetch=True)

    if not songs:
        print(f"Playlist '{p_name}' has no songs.")
        return
    print(f"\nSongs in playlist '{p_name}':")
    for i, (suid, title, artist) in enumerate(songs, start=1):
        print(f"{i}. {title} — {artist}")

    try:
        selection = int(input("Enter the number of the song to remove: ").strip())
        if not (1 <= selection <= len(songs)):
            print("Invalid selection.")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    suid, title, artist = songs[selection - 1]
    confirm = input(f"Remove '{title}' by {artist} from '{p_name}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Canceled.")
        return

    # Step 5: Delete from addedsongto
    query("DELETE FROM addedsongto WHERE pid = %s AND suid = %s;", (pid, suid))
    print(f"Removed '{title}' by {artist} from playlist '{p_name}'.")
  
def list_user_playlists(uid):
  playlists = query("""SELECT p.pid, p.name,
              COUNT(a.suid) AS num_songs,
              COALESCE(SUM(split_part(s.length, ':', 1)::int * 60 +
              split_part(s.length, ':', 2)::int), 0) AS total_duration
              FROM playlist p
              LEFT JOIN addedsongto a ON p.pid = a.pid
              LEFT JOIN song s ON a.suid = s.suid
              WHERE p.uid = %s
              GROUP BY p.pid, p.name
              ORDER BY p.name ASC""", (uid,), fetch=True)
  if not playlists:
    print("You have no playlists.")
    return []
  print("\nYour Playlists:")
  for idx, pl in enumerate(playlists, start=1):
    total_minutes = pl[3] // 60
    total_duration_remaining_seconds = pl[3] % 60
    print(f"{idx}. {pl[1]} - {pl[2]} songs, {total_minutes}:{total_duration_remaining_seconds:02d} min")
  return playlists

def find_album(name):
  name = name.strip().replace("'", "''")
  return query("SELECT alid, title FROM album WHERE title ILIKE %s ORDER BY title ASC", (f"%{name}%",), fetch=True)

def select_album():
  name_input = input("Enter album name here: ").strip()
  results = find_album(name_input)
  if not results:
    print("No album with that name")
    return 
  if len(results) == 1:
    return results[0][0]
  print("Multiple albums found")
  for i in range(len(results)):
    album_id = results[i][0]
    album_name = results[i][1]
    print(f"{i + 1}. {album_name} (ID: {album_id})")
  selection = input("Enter number for desired album: ")
  try:
      selection = int(selection)
      if 1 <= selection <= len(results):
          return results[selection - 1][0]
      else:
          print("Invalid selection.")
          return None
  except Exception:
      print("Please enter a valid number.")
      return None
    

def add_album_to_playlist(uid):
  p_name = input("Enter name of playlist: ").strip()
  if not p_name:
    print("Empty playlist name")
    return
  pid = get_pid(p_name, uid)
  if not pid:
    print(f"Playlist {p_name} does not exist")
    return
  alid = select_album()
  album_name = query(f"SELECT title FROM album WHERE alid= {alid}", True)[0][0]
  if not alid:
      return
  query("INSERT INTO addedalbumto (pid, alid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (pid, alid))
  songs = query("SELECT suid FROM containsas WHERE alid = %s;", (alid,), fetch=True)
  if not songs:
      print("No songs found in that album.")
      return
  for (suid,) in songs:
      query("INSERT INTO addedsongto (pid, suid) VALUES (%s, %s) ON CONFLICT DO NOTHING;", (pid, suid))

  print(f"Album {album_name} and its {len(songs)} songs added to playlist '{p_name}'.")
  print("Album added to playlist.")

def remove_album_from_playlist(uid):
    p_name = input("Enter playlist name here: ").strip()
    if not p_name:
        print("Empty playlist name.")
        return

    pid = get_pid(p_name, uid)
    if not pid:
        print(f"Playlist '{p_name}' does not exist.")
        return

    # Step 2: Get all albums currently in this playlist
    albums = query("""
        SELECT aa.alid, al.title
        FROM addedalbumto aa
        JOIN album al ON aa.alid = al.alid
        WHERE aa.pid = %s
        ORDER BY al.title ASC;
    """, (pid,), fetch=True)

    if not albums:
        print(f"No albums found in playlist '{p_name}'.")
        return
    if len(albums) == 1:
        alid, alname = albums[0]
        confirm = input(f"Remove '{alname}' from '{p_name}'? (y/n): ").strip().lower()
        if confirm != "y":
            print("Canceled.")
            return
    else:
        print(f"\nAlbums in '{p_name}':")
        for i, (alid, alname) in enumerate(albums, start=1):
            print(f"{i}. {alname} (ID: {alid})")

        try:
            selection = int(input("Enter the number of the album to remove: ").strip())
            if 1 <= selection <= len(albums):
                alid, alname = albums[selection - 1]
            else:
                print("Invalid selection.")
                return
        except ValueError:
            print("Please enter a valid number.")
            return
    in_playlist = query(
        "SELECT 1 FROM addedalbumto WHERE pid = %s AND alid = %s;",
        (pid, alid),
        fetch=True
    )
    if not in_playlist:
        print(f"Album '{alname}' is not in this playlist.")
        return

    # Step 5: Remove the album record
    query("DELETE FROM addedalbumto WHERE pid = %s AND alid = %s;", (pid, alid))

    # Step 6: Remove all songs from this album from the playlist
    query("""
        DELETE FROM addedsongto
        WHERE pid = %s
          AND suid IN (SELECT suid FROM containsas WHERE alid = %s);
    """, (pid, alid))

    print(f"Removed album '{alname}' and all its songs from playlist '{p_name}'.")
  
