from database_manip.users import create_user, login_user, follow_user, unfollow_user, search_users_by_email, slime_user
from database_manip.playlists import (create_playlist, list_user_playlists, add_song_to_playlist, 
                         remove_song_from_playlist, rename_playlist, slime_playlist, 
                         play_playlist, add_album_to_playlist, remove_album_from_playlist)
from database_manip.songs import search_songs, rate_song, song_played

def main():
    print("Music App Database")
    
    uid = None
    
    while not uid:
        print("\n1. Login\n2. Create Account\n3. Exit")
        choice = input("Select: ").strip()
        
        if choice == "1" or choice == "1.":
            uid = login_user()
            
        elif choice == "2" or choice == "2.":
            uid = create_user()
            
        elif choice == "3" or choice == "3.":
            print("Goodbye!")
            return
        else:
            print("Invalid choice.")
    
    while True:
        print("\n")
        print("MAIN MENU")
        print("""
1.  Search songs
2.  Listen to song
3.  Rate song
4.  View my playlists
5.  Create playlist
6.  Rename playlist
7.  Delete playlist
8.  Add song to playlist
9.  Remove song from playlist
10. Add album to playlist
11. Remove album from playlist
12. Play entire playlist
13. Search users by email
14. Follow user
15. Unfollow user
16. Delete account
0.  Logout
        """)
        
        choice = input("Select: ").strip()
        
        if choice == "1" or choice == "1.":
            # Search songs
            search_songs()
                
        elif choice == "2" or choice == "2.":
            # Listen to song
            song_identifier = input("Enter song ID or song title: ").strip()
            song_played(uid, song_identifier)
            
        elif choice == "3" or choice == "3.":
            # Rate song
            song_identifier = input("Enter song ID or song title: ").strip()
            try:
                stars = int(input("Stars (1-5): ").strip())
                rate_song(uid, song_identifier, stars)
            except ValueError:
                print("Invalid rating. Must be a number.")
                
        elif choice == "4" or choice == "4.":
            # View playlists
            list_user_playlists(uid)
            
        elif choice == "5" or choice == "5.":
            # Create playlist
            create_playlist(uid)
            
        elif choice == "6" or choice == "6.":
            # Rename playlist
            rename_playlist(uid)
            
        elif choice == "7" or choice == "7.":
            # Delete playlist
            slime_playlist(uid)
                
        elif choice == "8" or choice == "8.":
            # Add song to playlist
            add_song_to_playlist(uid)
            
        elif choice == "9" or choice == "9.":
            # Remove song from playlist
            remove_song_from_playlist(uid)
            
        elif choice == "10" or choice == "10.":
            # Add album to playlist
            add_album_to_playlist(uid)
            
        elif choice == "11" or choice == "11.":
            # Remove album from playlist
            remove_album_from_playlist(uid)
            
        elif choice == "12" or choice == "12.":
            # Play playlist
            play_playlist(uid)
            
        elif choice == "13" or choice == "13.":
            # Search users by email
            search_users_by_email()
            
        elif choice == "14" or choice == "14.":
            # Follow user
            follow_user(uid)
            
        elif choice == "15" or choice == "15.":
            # Unfollow user
            unfollow_user(uid)
        
        elif choice == "16" or choice == "16.":
            # Delete account
            slime_user(uid)
            
        elif choice == "0" or choice == "0.":
            print("Logging out. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()