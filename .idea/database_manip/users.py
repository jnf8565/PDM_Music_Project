from datetime import date
from database_manip.cursor import query

def valid_email(email) -> bool:
    # Handling for improper number or location of @ symbol
    if email.count('@') != 1:
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
    while exists or not username or username == "":
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

    query(f"""
        INSERT INTO users (last_access_date, username, password, first_name, last_name, email)
        VALUES ('{created_on}', '{username}', '{password}', '{fname}', '{lname}', '{email}')
        """)
    print(f"created user '{username}'")
    
def username_exists(username):
    count = query(f"""
                    SELECT COUNT(*)
                    FROM users
                    WHERE (username = '{username}')
                    """, True)
    if count[0][0] > 0:
        return True
    else:
        return False
    
def email_exists(email):
    count = query(f"""
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE email = '{email}'
                    """ , True)
    if count[0][0] > 0:
        return True
    else:
        return False

def login_user():
    
    # Handling for username
    username = input("Enter username: ").strip()
    exists = username_exists(username)
    while not username or not exists:
        if not exists:
            print("No user with this username")
        else:
            print("Username cannot be empty")
        username = input("Enter username: ").strip()
        exists = username_exists(username)
    
    # Handling for password
    password = input("Enter a password for the account: ").strip()
    stored_pws = query(f"""
               SELECT password 
               FROM users
               WHERE (username = '{username}')
               """, True)
    while password != stored_pws[0][0]:
        print("Invalid password")
        password = input("Enter password: ").strip()

    uid = query(f"""
                SELECT uid
                FROM users
                WHERE (username = '{username}' AND password = '{password}')
                """, True)
    if uid:
        print("Logged in")
        return uid[0][0]
    else:
        print("No such user exists")


def search_users_by_email():
    term = input("Enter search term for email: ").strip()
    while not term:
        print("Term cannot be empty.")
    
    emails = query(f"""
                   SELECT email
                   FROM users
                   WHERE LOWER(username) LIKE LOWER('{term}')
                   ORDER BY LOWER(username) ASC
                   """, True)
    return emails


def follow_user(follower_id):
    username = input("Enter the username of the account to follow: ").strip()
    followee_id = get_uid(username)
    if not followee_id:
        print("User not found.")
        return
    followee_id = followee_id[0][0]
    
    already_following = query(f"""
                              SELECT COUNT(*)
                              FROM follows
                              WHERE (follower = {follower_id} AND followed = {followee_id})
                              """, True)
    count = already_following[0][0]
    if count > 0:
        print("Already following this user.")
        return
    
    query(f"""
          INSERT INTO follows(follower, followed)
          VALUES ({follower_id}, {followee_id})
          """)
    print("User followed successfully.")

def unfollow_user(follower_id):

    username = input("Enter the username of the account to unfollow: ").strip()
    followee_id = query(f"""
                        SELECT uid
                        FROM users
                        WHERE (username = '{username}')
                        """, True)
    if not followee_id:
        print("User not found.")
        return
    followee_id = followee_id[0][0]
    
    already_following = query(f"""
                              SELECT COUNT(*)
                              FROM follows
                              WHERE (follower = {follower_id} AND followed = {followee_id})
                              """, True)
    if already_following[0][0] == 0:
        print("This user was not being followed.")
        return
    elif not already_following:
        print("Followee does not exist")
    
    query(f"""
          DELETE FROM follows
          WHERE (follower = {follower_id} AND followed = {followee_id})
          """)
    print("User unfollowed successfully.")
    
    
def get_uid(username):
    return_id = query(f"""
                SELECT uid
                FROM users
                WHERE (username = '{username}')
                """, True)
    if not return_id:
        print("User does not exist.")
    return return_id


def delete_user(uid):
    confirm = input("Are you sure you want to delete this account? yes/no").strip().lower()

    if confirm == "yes":
        query(f"""
              DELETE FROM users
              WHERE (uid = {uid})
              """)
    
    print("Successfully deleted user.")