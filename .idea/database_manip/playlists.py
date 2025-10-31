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
  for album in results:
      album_id = album[0]     # The album’s ID
      album_title = album[1]  # The album’s title
      print(f"{index}. {album_title} (ID: {album_id})")
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
     print(f"Playlist {p_name} does not exist")
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
  p_name = input("Enter playlist name here: ")
  if not p_name:
    print("Empty playlist name")
    return
  pid = get_pid(p_name, uid)
  if not pid:
    print(f"Playlist {p_name} does not exist")
    return
  suid = select_song()
  if not suid:
     return
  query(f"DELETE FROM addedsongto WHERE pid={pid} AND suid={suid}")
  print("Song removed from playlist")
  
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
  print("Album added to playlist.")

def remove_album_from_playlist(uid):
  p_name = input("Enter playlist name here: ")
  if not p_name:
    print("Empty playlist name")
    return
  pid = get_pid(p_name, uid)
  if not pid:
    print(f"Playlist {p_name} does not exist")
    return
  alid = select_album()
  in_playlist = query(
        f"SELECT 1 FROM addedalbumto WHERE pid = {pid} AND alid = {alid}",
        fetch=True
        )
  if not in_playlist:
      print("That album is not in this playlist.")
      return
  if not alid:
     return
  query(f"DELETE FROM addedalbumto WHERE pid={pid} AND alid={alid}")
  print("Album removed from playlist")
