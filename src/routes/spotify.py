from bson import ObjectId

def get_album_data(mongo_db, album_id):
    result = mongo_db.find_one({"_id": ObjectId(album_id)})
    if not result:
        pass
        # query spotify API
    print(result)
    return result
