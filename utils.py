import sqlite3


def get_images(ad_id: str):
    images = sqlite3.connect("Users.db").execute("SELECT image_path FROM post_images WHERE post_id = ?",
                                                 (ad_id,)).fetchall()
    images = [i[0] for i in images]

    return images


def get_ad(ad_id: str):
    if ad_id is None:
        return {}
    print(ad_id)
    ad = sqlite3.connect('Users.db').execute("SELECT * FROM Ad WHERE ad_id = ?", (ad_id,)).fetchone()
    ad = {
        "title": ad[0],
        "category":ad[1],
        "state":ad[2],
        "city":ad[3],
        "author":ad[4],
        "ISBN":ad[5],
        "username":ad[6],
        "price":ad[7],
        "desc":ad[8],
        "ad_id":ad[9],
        "age_group":ad[10],
        "status":ad[11],
        "date":ad[12],
        "views":ad[13],
        "images":get_images(ad_id)
    }
    return ad


def search(params: {str: str}) -> {str:str}:
    con = sqlite3.connect("Users.db")
    con.set_trace_callback(print)
    ads = con.cursor().execute('''
                            SELECT ad_id FROM Ad WHERE UPPER(domain) LIKE ? AND 
                            status = 'Active' AND
                            UPPER(age_group) LIKE ? AND 
                            UPPER(state) LIKE ? AND 
                            UPPER(ISBN) LIKE ? AND 
                            UPPER(author) LIKE ? AND 
                            price <= ? AND 
                            (UPPER(title) LIKE ? OR 
                            UPPER(desc) LIKE ?)
                            ORDER BY date DESC
                          ''',
                               [
                                   f'%{params.get("domain").upper()}%' if not params.get("domain","Any") == 'Any' else '%',
                                   f'%{params.get("age-group").upper()}%' if not params.get("age-group","Any") == 'Any' else '%',
                                   f'%{params.get("state").upper()}%' if not params.get("state","Any") == 'Any' else '%',
                                   f'{params.get("ISBN").upper()}' if not params.get("ISBN","") == '' else '%',
                                   f'%{params.get("author").upper()}%' if not params.get("author","") == '' else '%',
                                   f'{int(params.get("max","5000"))}' if not params.get("max",'5000') == '' else '%',
                                   f'%{params.get("text").upper()}%' if not params.get("text","") == '' else '%',
                                   f'%{params.get("text").upper()}%' if not params.get("text","") == '' else '%',
                               ]
                               )
    ads = [get_ad(ad[0]) for ad in ads]
    return ads

def get_user(username: str) -> {str:str}:
    con = sqlite3.connect("Users.db")
    user = con.execute("SELECT * FROM Users WHERE username = ?",[username]).fetchall()


