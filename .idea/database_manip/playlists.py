from cursor import query
import psycopg2

def create_playlist(uid):
  try:
      playlist_name = input("Enter playlist name here: ").strip()
      if not playlist_name:
        print("Empty playlist name")
        return
      pid = query(f"INSERT INTO playlist (name) VALUES ('{playlist_name}') RETURNING pid", fetch=True)[0][0]
      if pid is not None:
        query(f"INSERT INTO createsp VALUES ({uid},{pid})")
        print(f"Playlist {playlist_name} created")
        return pid
      else:
        print("PID not found for playlist")
        return None
  except  psycopg2.errors.UniqueViolation as e:
     print("Playlists cannot have duplicate names")
     exit
  except Exception as e:
     print("Database error")
     exit

def get_pid(p_name):
  p_name = p_name.strip()
  result = query(f"SELECT pid FROM playlist WHERE name='{p_name}'", fetch=True)
  if result:
      return result[0][0]
  else:
      return None

def rename_playlist():
  old_name = input("Enter current name of playlist here: ").strip()
  pid = get_pid(old_name)
  if not pid:
       print(f"Playlist '{old_name}' does not exist")
       return
  new_name = input("Enter new name of playlist here: ").strip()
  if not new_name:
       print("Empty playlist name")
       return
  query(f"UPDATE playlist SET name='{new_name}' WHERE pid={pid}")
  print(f"Playlist '{old_name}' changed to '{new_name}'")
  
       

def delete_playlist():
  name = input("Enter name of playlist to be deleted: ").strip()
  pid = get_pid(name)
  if not pid:
       print(f"Playlist '{name}' does not exist")
       return
  query(f"DELETE FROM addedto WHERE pid={pid}")
  query(f"DELETE FROM listensto WHERE pid={pid}")
  query(f"DELETE FROM playlist WHERE pid={pid}")
  query(f"DELETE FROM createsp WHERE pid={pid}")
  print("Playlist deleted")

# def add_song_to_playlist(pid, sid):

# def play_playlist(pid, sid, uid):

# def remove_song_from_playlist(pid, sid):

# def list_user_playlists(uid):

