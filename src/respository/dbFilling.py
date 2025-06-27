import psycopg

def build_row(name: str, bank:str, points:bool, sub:str, prevArr: list[tuple]) -> list[tuple]:
    if(len(prevArr) == 0):
         prevArr = []

    prevArr.insert((name, bank, points, sub))

    return prevArr


def insert_batch(basic_data: list[tuple]):
    query:str = """ INSERT INTO maininfo 
    VALUES (%s, %s, %s), (name, bank, points, sub)
    """
    
    with psycopg.connect("dbname=rewardInfo") as conn:
        with conn.cursor() as db:

            db.executemany(query, basic_data)

            conn.commit()
