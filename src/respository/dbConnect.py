import psycopg

with psycopg.connect("dbname=rewardInfo") as conn:
    with conn.cursor() as db:

        query1 = """ CREATE TABLE mainInfo (
        id serial PRIMARY KEY,
        name text,
        bank text,
        points bool)
        """

        query2 = """ CREATE TABLE pointInfo (
            bank text PRIMARY KEY,
            multiplier numeric)
        """

        db.execute(query1)
        db.execute(query2)

        conn.commit()

print("Done!")