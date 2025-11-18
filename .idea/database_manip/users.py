from datetime import date, datetime
from database_manip.cursor import query
import os, hashlib, base64
import secrets

iterations = 100_000

def valid_email(email: str) -> bool:
    # Handling for improper number or location of @ symbol
    if email.count("@") != 1:
       return False
    at_loc = email.index('@')
    if at_loc == 0 or at_loc == len(email)-1:
       return False
    
    # Handling for lack or improper placement of . symbol
    if '.' not in email[at_loc + 1:]:
        return False
    if email.endswith('.'):
       return False
    
    return True

def create_user():
    
    # Handling for email
    email = input("Please enter the email for the account: ").strip()
    exists = email_exists(email)
    while exists or not email or not valid_email(email):
        if exists:
            print("This email is already in use.")
        else:
            print("Invalid email.")
        email = input("Please enter the email for the account: ").strip()
        exists = email_exists(email)
    
    # Handling for username
    username = input("Enter a username for the account: ").strip()
    exists = username_exists(username)
    while exists or not username:
        if exists:
            print("This username is already in use.")
        else:
            print("Username cannot be empty.")
        username = input("Enter a username for the account: ").strip()
        exists = username_exists(username)

    # Handling for password
    password = input("Enter a password for the account: ").strip()
    while not password:
        print("Password cannot be empty.")
        password = input("Enter a password for the account: ").strip()
    salt = os.urandom(16)
    hashed_pw = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    salt_b64 = base64.b64encode(salt).decode()
    hash_b64 = base64.b64encode(hashed_pw).decode()
    store = f"pdkdf2_sha256${iterations}${salt_b64}${hash_b64}"

    # Handling for first name
    fname = input("Enter your first name: ").strip()
    while not fname:
        print("First name cannot be empty.")
        fname = input("Enter your first name: ").strip()

    # Handling for last name
    lname = input("Enter your last name: ").strip()
    while not lname:
        print("Last name cannot be empty.")
        lname = input("Enter your last name: ").strip()
    
    created_at = date.today().strftime("%m/%d/%Y")
    query("""
         INSERT INTO users (last_access_date, username, password, first_name, last_name, email, date_time_created)
         VALUES (%s, %s, %s, %s, %s, %s, %s)
         """, (created_at, username, store, fname, lname, email, datetime.now().replace(microsecond=0).strftime("%m/%d/%Y %H:%M:%S")))
    #query(f"""
    #    INSERT INTO users (last_access_date, username, password, first_name, last_name, email, date_time_created)
    #    VALUES ('{created_at}', '{username}', '{hashed_pw}', '{fname}', '{lname}', '{email}', '{datetime.now().replace(microsecond=0).strftime("%m/%d/%Y %H:%M:%S")}')
    #    """)
    uid = query("""
                SELECT uid
                FROM users
                WHERE (email = %s)
                """, (email,), True)
    if uid:
        print(f"created user '{username}'")
        return uid[0][0]
    else:
        print("An error occurred while initializing the user.")
    
def username_exists(username):
    # count = query(f"""
    #                 SELECT COUNT(*)
    #                 FROM users
    #                 WHERE (username = (%s))
    #                 """, (username), True)
    count = query("""
                SELECT COUNT(*)
                FROM users
                WHERE (username = %s)
                """, (username,), True)
    if count and count[0][0] > 0:
        return True
    else:
        return False
    
def email_exists(email):
    # count = query(f"""
    #                 SELECT COUNT(*) 
    #                 FROM users 
    #                 WHERE email = ((%s))
    #                 """, (email), True)

    count = query("""
                SELECT COUNT(*) 
                FROM users 
                WHERE (email = %s)
                """, (email,), True)
    if count and count[0][0] > 0:
        return True
    else:
        return False

def login_user():

    # Handling for username
    username = input("Enter username: ").strip()
    user_data = query("""
                SELECT uid, username, password
                FROM users
                WHERE (username = %s)
                """, (username,), True)
    while not username or not user_data:
        if not user_data:
            print("No user with this username")
        else:
            print("Username cannot be empty")
        username = input("Enter username: ").strip()
        user_data = query("""
                SELECT uid, username, password
                FROM users
                WHERE (username = %s)
                """, (username,), True)
    
    # Handling for password
    password = input("Enter a password for the account: ").strip()
    algo, iter, salt_b64, hash_b64 = user_data[0][2].split('$')
    iter = int(iter)
    salt = base64.b64decode(salt_b64)
    stored_hash = base64.b64decode(hash_b64)
    cmp_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)

    while not secrets.compare_digest(cmp_hash, stored_hash):
        print("Invalid password")
        password = input("Enter password: ").strip()
        cmp_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
    
    uid = user_data[0][0]
    
    if uid:
        date_accessed = date.today().strftime("%m/%d/%Y")
        
        query("""
              UPDATE users
              SET last_access_date = %s
              WHERE uid = %s
              """, ( date_accessed, uid))


        print("Logged in")
        return uid
    else:
        print("No such user exists")


def search_users_by_email():
    term = input("Enter search term for email: ").strip()
    while not term:
        print("Term cannot be empty.")
    
    # emails = query(f"""
    #                SELECT email
    #                FROM users
    #                WHERE LOWER(username) LIKE LOWER((%s))
    #                ORDER BY LOWER(username) ASC
    #                """, (term), True)

    emails = query("""
                SELECT email
                FROM users
                WHERE LOWER(username) LIKE LOWER(%s)
                ORDER BY LOWER(username) ASC
                """, (term,), True)
    if not emails:
        print("No matches found")
        return
    for email in emails[0]:
        print(email + "\n")

def follow_user(follower_id):
    email = input("Enter the email of the account to follow: ").strip()
    followee_id = get_uid(email)
    if not followee_id:
        print("User not found.")
        return
    followee_id = followee_id
    
    # already_following = query(f"""
    #                           SELECT COUNT(*)
    #                           FROM follows
    #                           WHERE (follower = (%s) AND followed = (%s))
    #                           """, (follower_id, followee_id), True)
    already_following = query("""
                            SELECT COUNT(*)
                            FROM follows
                            WHERE (follower = %s AND followed = %s)
                            """, (follower_id, followee_id), True)
    if already_following and already_following[0][0] > 0:
        print("Already following this user.")
        return
    
    # query(f"""
    #       INSERT INTO follows(follower, followed)
    #       VALUES ((%s), (%s))
    #       """, (follower_id, followee_id))
    query("""
        INSERT INTO follows(follower, followed)
        VALUES (%s, %s)
        """, (follower_id, followee_id))
    print("User followed successfully.")

def unfollow_user(follower_id):

    email = input("Enter the email of the account to unfollow: ").strip()
    # followee_id = query(f"""
    #                     SELECT uid
    #                     FROM users
    #                     WHERE (username = (%s))
    #                     """, (username), True)
    followee_id = query("""
                    SELECT uid
                    FROM users
                    WHERE (email = %s)
                    """, (email,), True)
    if not followee_id:
        print("User not found.")
        return
    followee_id = followee_id[0][0]
    
    # already_following = query(f"""
    #                           SELECT COUNT(*)
    #                           FROM follows
    #                           WHERE (follower = (%s) AND followed = (%s))
    #                           """, (follower_id, followee_id), True)
    already_following = query("""
                            SELECT COUNT(*)
                            FROM follows
                            WHERE (follower = %s AND followed = %s)
                            """, (follower_id, followee_id), True)
    if not already_following:
        print("This user was not being followed.")
        return
    elif already_following[0][0] == 0:
        print("User with this email does not exist")
        return
    
    # query(f"""
    #       DELETE FROM follows
    #       WHERE (follower = (%s) AND followed = (%s))
    #       """, (follower_id, followee_id))
    query("""
        DELETE FROM follows
        WHERE (follower = %s AND followed = %s)
        """, (follower_id, followee_id))
    print("User unfollowed successfully.")
    
    
def get_uid(email):
    # return_id = query(f"""
    #             SELECT uid
    #             FROM users
    #             WHERE (username = (%s))
    #             """, (username), True)
    return_id = query("""
            SELECT uid
            FROM users
            WHERE (email = %s)
            """, (email,), True)
    if not return_id:
        print("User does not exist.")
    return return_id[0][0]


def slime_user(uid):
    confirm = input("Are you sure you want to delete this account? yes/no\n").strip().lower()

    if confirm == "yes":
        # query(f"""
        #       DELETE FROM users
        #       WHERE (uid = (%s))
        #       """, (uid))
            #            s.Title AS Song,
            #    a.Name  AS Artist,
            #    al.Title AS Album,
            #    s.Length,
        query("""
              DELETE FROM follows
              WHERE(follower = %s)
              """, (uid,))
        query("""
                DELETE FROM users
                WHERE (uid = %s)
                """, (uid,))
        print("Successfully deleted user.")
    else:
        print("Cancelling deletion.")
