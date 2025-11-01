from users import create_user, login_user, follow_user, unfollow_user, slime_user

if __name__ == "__main__":
    id = login_user()
    follow_user(id)
    unfollow_user(id)
    slime_user(id)