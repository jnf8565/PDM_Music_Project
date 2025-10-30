from cursor import query

def create_playlist(uid):
  playlist_name = input("Enter playlist name here: ").strip()
  while not playlist_name:
      print("Empty playlist name")
      playlist_name = input("Enter playlist name here: ").strip()
  pid = query(f"INSERT INTO playlist (name) VALUES ('{playlist_name}') RETURNING pid", fetch=True)[0][0]
  if pid is not None:
      query(f"INSERT INTO createsp VALUES ({uid},{pid})")
      print(f"Playlist {playlist_name} created")
      return pid
  else:
      print("PID not found for playlist")
      return None

def get_pid(p_name):
  p_name = p_name.strip()
  result = query(f"SELECT pid FROM playlist WHERE name='{p_name}'", fetch=True)
  if result:
      return result[0][0]
  else:
      return None

def rename_playlist():
  old_name = input("Enter current name of playlist here: ")
  pid = get_pid(old_name)
  while not pid:
       print(f"Playlist '{old_name}' does not exist")
       old_name = input("Enter current name of playlist here: ")
  new_name = input("Enter new name of playlist here: ")
  while not new_name:
       print("Empty playlist name")
       new_name = input("Enter current name of playlist here: ")
  query(f"UPDATE playlist SET name='{new_name}' WHERE pid={pid}")
  print(f"Playlist '{old_name}' changed to '{new_name}'")
  
       

def delete_playlist():
  name = input("Enter name of playlist to be deleted: ")
  pid = get_pid(name)
  while not pid:
       print(f"Playlist '{name}' does not exist")
       name = input("Enter name of playlist to be deleted: ")
  query(f"DELETE FROM addedto WHERE pid={pid}")
  query(f"DELETE FROM listensto WHERE pid={pid}")
  query(f"DELETE FROM playlist WHERE pid={pid}")
  query(f"DELETE FROM createsp WHERE pid={pid}")
  print("Playlist deleted")

# def add_song_to_playlist(pid, sid):

# def play_playlist(pid, sid, uid):

# def remove_song_from_playlist(pid, sid):

# def list_user_playlists(uid):

