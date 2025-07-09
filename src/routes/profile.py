


def get_profile_data(mongo_db, username):
    query = {"username": username}
    return mongo_db.find_one(query)