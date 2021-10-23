import sqlite3
def get_images(ad_id: str):
    images = sqlite3.connect("Users.db").execute("SELECT image_path FROM post_images WHERE post_id = ?",(ad_id,)).fetchall()
    images = [i[0] for i in images]

    return images
