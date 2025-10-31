from datetime import date
from cursor import query

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

    created_on = date.today()

    return query(f"""
        INSERT INTO users (last_access_date, username, password, first_name, last_name, email)
        VALUES ({created_on}, {username}, {password}, {fname}, {lname}, {email})
        RETURNING uid
        """)
    
def username_exists(username):
    exists = query(f"""
                    SELECT username
                    FROM users
                    WHERE (username = '{username}')
                    """, True)
    if exists:
        return True
    else:
        return False
    
def email_exists(email):
    exists = query(f"""
                    SELECT email
                    FROM users
                    WHERE (email = '{email}')
                    """, True)
    if exists:
        return True
    else:
        return False

def login_user():
    
    # Handling for username
    username = print("Enter username: ").strip()
    exists = username_exists(username)
    while not username or not exists:
        if not exists:
            print("No user with this username")
        else:
            print("Username cannot be empty")
        username = print("Enter username: ").strip()
        exists = username_exists(username)
    
    # Handling for password
    password = input("Enter a password for the account: ").strip()
    stored_pws = query(f"""
               SELECT password 
               FROM users
               WHERE (username = '{username}')
               """, True)
    while password not in stored_pws:
        print("Invalid password")
        password = print("Enter password: ").strip()

    uid = query(f"""
                SELECT uid
                FROM users
                WHERE (username = '{username}' AND password = '{password}')
                """, True)
    if uid:
        return uid
    else:
        print("No such user exists")


def search_users_by_email():
    term = input("Enter search term for email: ").strip()
    while not term:
        print("Term cannot be empty.")
    
    emails = query(f"""
                   SELECT email
                   FROM users
                   WHERE LOWER(username) LIKE LOWER({term}))
                   ORDER BY LOWER(username) ASC
                   """, True)
    return emails


def follow_user(follower_id, followee_id):
    already_following = query(f"""
                              SELECT COUNT(*)
                              FROM follows
                              WHERE (follows = {follower_id} AND followed = {followee_id})
                              """)
    
    if already_following:
        print("Already following this user.")
        return
    
    query(f"""
          INSERT INTO follows(follows, followed)
          VALUES ({follower_id}, {followee_id})
          """)

def unfollow_user(follower_id, followee_id):
    already_following = query(f"""
                              SELECT COUNT(*)
                              FROM follows
                              WHERE (follows = {follower_id} AND followed = {followee_id})
                              """)
    
    if already_following == 0:
        print("This user was not being followed.")
        return
    elif not already_following:
        print("Followee does not exist")
    
    query(f"""
          DELETE FROM follows
          WHERE (follows = {follower_id} AND followed = {followee_id})
          """)
    
    
def get_uid(uid):
    return_id = query(f"""f
                SELECT uid
                FROM users
                WHERE (uid = {uid})
                """)
    if not return_id:
        print("User does not exist.")
    return return_id


def delete_user(uid):
    confirm = input("Are you sure you want to delete this account? yes/no").strip().lower()

    if confirm == "yes":
        query(f"""f
              DELETE FROM users
              WHERE (uid = {uid})
              """)
