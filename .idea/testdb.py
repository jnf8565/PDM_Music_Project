from cursor import query

query("INSERT into testusers (email, password) VALUES ('steve@gmail.com', '1234');")
print("inserted user")
