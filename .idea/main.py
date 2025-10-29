from users import create_user, login_user, follow_user, unfollow_user
from collections import create_playlist, list_playlists, add_song_to_playlist, remove_song_from_playlist
from songs import search_songs, rate_song, listen_to_song

def main():
    print("Welcome to MusicApp")

    uid = None
    while not uid:
        print("\n1. Login\n2. Create Account\n3. Exit")
        choice = input("Select: ")
        if choice == "1":
            uid = login_user(input("Username: "), input("Password: "))
        elif choice == "2":
            uid = create_user(
                input("Username: "),
                input("Password: "),
                input("First name: "),
                input("Last name: "),
                input("Email: ")
            )
        else:
            return

    while True:
        print("""
1. Search songs
2. Listen to song
3. Rate song
4. View playlists
5. Create playlist
6. Add song to playlist
7. Remove song from playlist
8. Follow user
9. Unfollow user
0. Exit
        """)
        choice = input("Select: ")
        if choice == "1":
            search_songs(input("Search term: "))
        elif choice == "2":
            listen_to_song(uid, input("Song ID: "))
        elif choice == "3":
            rate_song(uid, input("Song ID: "), int(input("Stars (1–5): ")))
        elif choice == "4":
            list_playlists(uid)
        elif choice == "5":
            create_playlist(uid, input("Playlist name: "))
        elif choice == "6":
            add_song_to_playlist(input("Playlist ID: "), input("Song ID: "))
        elif choice == "7":
            remove_song_from_playlist(input("Playlist ID: "), input("Song ID: "))
        elif choice == "8":
            follow_user(uid, input("User ID to follow: "))
        elif choice == "9":
            unfollow_user(uid, input("User ID to unfollow: "))
        else:
            break

if __name__ == "__main__":
    main()