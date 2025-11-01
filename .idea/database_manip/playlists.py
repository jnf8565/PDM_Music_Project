from database_manip.cursor import query
import psycopg2

def create_playlist(uid):
  try:
      playlist_name = input("Enter playlist name here: ").strip()
      if not playlist_name:
        print("Empty playlist name")
        return
      pid = query(f"INSERT INTO playlist (name,uid) VALUES ('{playlist_name}',{uid}) RETURNING pid", fetch=True)[0][0]
      if pid is not None:
        query(f"INSERT INTO createsp VALUES ({uid},{pid})")
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
  p_name = p_name.strip()
  result = query(f"SELECT pid FROM playlist WHERE name='{p_name}' AND uid={uid}", fetch=True)
  if result:
      return result[0][0]
  else:
      return None

def rename_playlist(uid):
  try:
    old_name = input("Enter current name of playlist here: ").strip()
    pid = get_pid(old_name,uid)
    if not pid:
          print(f"Playlist '{old_name}' does not exist")
          return
    new_name = input("Enter new name of playlist here: ").strip()
    if not new_name:
          print("Empty playlist name")
          return
    query(f"UPDATE playlist SET name='{new_name}' WHERE pid={pid}")
    print(f"Playlist '{old_name}' changed to '{new_name}'")
  except Exception:
     print("Playlist with that name already exists")
  
def find_song(name):
  name = name.strip().replace("'", "''")
  return query(f"SELECT suid, title, artist FROM song WHERE title ILIKE '%{name}%' ORDER BY title ASC", fetch=True)

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
  for song in results:    # The album’s ID
      song_title = song[1]  # The album’s title
      song_artist = song[2]
      print(f"{index}. {song_title} by {song_artist}")
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
  query(f"DELETE FROM addedsongto WHERE pid={pid}")
  query(f"DELETE FROM addedalbumto WHERE pid={pid}")
  query(f"DELETE FROM createsp WHERE pid={pid}")
  query(f"DELETE FROM playlist WHERE pid={pid}")
  print("Playlist deleted")

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
  query(f"INSERT INTO addedsongto (pid, suid) VALUES ({pid}, {suid}) ON CONFLICT DO NOTHING;")
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
  songs = query(f"""
        SELECT s.suid, s.title, s.artist
        FROM addedsongto a
        JOIN song s ON a.suid = s.suid
        WHERE a.pid = {pid}
        ORDER BY s.title ASC;
    """, fetch=True)
  if not songs:
     print("Empty playlist")
     return
  print(f"\nPlaying playlist '{playlists[selection - 1][1]}':")
  for s in songs:
      suid, title, artist = s
      print(f"Now playing: {title} by {artist}")
      query(f"""
          INSERT INTO listensto (uid, suid, starttime)
          VALUES ({uid}, {suid}, NOW())
          ON CONFLICT DO NOTHING;
      """)
  print("Finished playing playlist.")
   

def remove_song_from_playlist(uid):
    # Step 1: Choose playlist
    p_name = input("Enter playlist name here: ").strip()
    if not p_name:
        print("Empty playlist name.")
        return

    pid = get_pid(p_name, uid)
    if not pid:
        print(f"Playlist '{p_name}' does not exist.")
        return

    # Step 2: Get all songs currently in the playlist
    songs = query(f"""
        SELECT s.suid, s.title, a.name AS artist
        FROM addedsongto ad
        JOIN song s ON ad.suid = s.suid
        JOIN createss cs ON s.suid = cs.suid
        JOIN artist a ON cs.aruid = a.aruid
        WHERE ad.pid = {pid}
        ORDER BY s.title ASC;
    """, fetch=True)

    if not songs:
        print(f"Playlist '{p_name}' has no songs.")
        return

    # Step 3: Let user pick which song to remove
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

    # Step 4: Confirm deletion
    confirm = input(f"Remove '{title}' by {artist} from '{p_name}'? (y/n): ").strip().lower()
    if confirm != "y":
        print("Canceled.")
        return

    # Step 5: Delete from addedsongto
    query(f"DELETE FROM addedsongto WHERE pid = {pid} AND suid = {suid};")
    print(f"Removed '{title}' by {artist} from playlist '{p_name}'.")
  
def list_user_playlists(uid):
  playlists = query(f"""SELECT p.pid, p.name,
              COUNT(a.suid) AS num_songs,
              COALESCE(SUM(split_part(s.length, ':', 1)::int * 60 +
              split_part(s.length, ':', 2)::int), 0) AS total_duration
              FROM playlist p
              LEFT JOIN addedsongto a ON p.pid = a.pid
              LEFT JOIN song s ON a.suid = s.suid
              WHERE p.uid = {uid}
              GROUP BY p.pid, p.name
              ORDER BY p.name ASC""", fetch=True)
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
  return query(f"SELECT alid, title FROM album WHERE title ILIKE '%{name}%' ORDER BY title ASC", fetch=True)

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
  if not alid:
      return
  query(f"INSERT INTO addedalbumto (pid, alid) VALUES ({pid}, {alid}) ON CONFLICT DO NOTHING;")
  songs = query(f"SELECT suid FROM containsas WHERE alid = {alid};", fetch=True)
  if not songs:
      print("No songs found in that album.")
      return
  
  # 3️⃣ Add each song to playlist
  for (suid,) in songs:
      query(f"INSERT INTO addedsongto (pid, suid) VALUES ({pid}, {suid}) ON CONFLICT DO NOTHING;")

  print(f"Album (ALID {alid}) and its {len(songs)} songs added to playlist '{p_name}'.")
  print("Album added to playlist.")

def remove_album_from_playlist(uid):
    # Step 1: Get playlist name
    p_name = input("Enter playlist name here: ").strip()
    if not p_name:
        print("Empty playlist name.")
        return

    pid = get_pid(p_name, uid)
    if not pid:
        print(f"Playlist '{p_name}' does not exist.")
        return

    # Step 2: Get all albums currently in this playlist
    albums = query(f"""
        SELECT aa.alid, al.title
        FROM addedalbumto aa
        JOIN album al ON aa.alid = al.alid
        WHERE aa.pid = {pid}
        ORDER BY al.title ASC;
    """, fetch=True)

    if not albums:
        print(f"No albums found in playlist '{p_name}'.")
        return

    # Step 3: Let the user pick which album to remove
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

    # Step 4: Verify album is actually in playlist
    in_playlist = query(
        f"SELECT 1 FROM addedalbumto WHERE pid = {pid} AND alid = {alid};",
        fetch=True
    )
    if not in_playlist:
        print(f"Album '{alname}' is not in this playlist.")
        return

    # Step 5: Remove the album record
    query(f"DELETE FROM addedalbumto WHERE pid = {pid} AND alid = {alid};")

    # Step 6: Remove all songs from this album from the playlist
    query(f"""
        DELETE FROM addedsongto
        WHERE pid = {pid}
          AND suid IN (SELECT suid FROM containsas WHERE alid = {alid});
    """)

    print(f"Removed album '{alname}' and all its songs from playlist '{p_name}'.")
  
