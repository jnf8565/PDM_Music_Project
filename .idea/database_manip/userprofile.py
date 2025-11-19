from database_manip.cursor import query


def get_collection_count(uid: int):
    result = query(f"""
        SELECT COUNT(*)
        FROM Playlist
        WHERE UID = {uid};
    """, fetch=True)
    return result[0][0] if result else 0


def get_follower_count(uid: int):
    result = query(f"""
        SELECT COUNT(*)
        FROM Follows
        WHERE Followed = {uid};
    """, fetch=True)
    return result[0][0] if result else 0


def get_following_count(uid: int):
    result = query(f"""
        SELECT COUNT(*)
        FROM Follows
        WHERE Follower = {uid};
    """, fetch=True)
    return result[0][0] if result else 0


def get_top_10_artists(uid: int):
    result = query(f"""
        SELECT a.ARUID,
               a.Name,
               COUNT(*) AS play_count
        FROM ListensTo l
        JOIN Song s ON l.SUID = s.SUID
        JOIN CreatesS cs ON s.SUID = cs.SUID
        JOIN Artist a ON cs.ARUID = a.ARUID
        WHERE l.UID = {uid}
        GROUP BY a.ARUID, a.Name
        ORDER BY play_count DESC
        LIMIT 10;
    """, fetch=True)
    return result if result else []


def view_user_profile(uid: int):
    collections = get_collection_count(uid)
    followers = get_follower_count(uid)
    following = get_following_count(uid)
    top_artists = get_top_10_artists(uid)

    print("\n USER PROFILE:\n")
    print(f"User ID: {uid}")
    print(f"Collections Owned: {collections}")
    print(f"Followers: {followers}")
    print(f"Following: {following}\n")

    print("Top 10 Artists:")
    if not top_artists:
        print("  No artist activity found.")
    else:
        for rank, (name, plays) in enumerate(top_artists, start=1):
            print(f"  {rank}. {name} — {plays} plays")
