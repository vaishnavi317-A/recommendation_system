import random
import sqlite3



DB_PATH="friendfinder.db"


CITIES =["BHOPAL","INDORE","DEHLI","MUMBAI","PUNE","JAIPUR"]
INTERESTS=["coding","music","travel","gaming","cricket","photography","movies","fitness","books","food"]
FIRST_NAMES=["asha","ravi","riya","karan","sneha","rohit","isha","pooja","sahiL","nikhil","kavya","dev","zoya","meera","Rohit","neha","vikram"]


def get_connection():
    return sqlite3.connect(DB_PATH)
def create_tables(conn):
    conn.executescript("""
                       DROP TABLE IF EXISTS follows;
                       DROP TABLE IF EXISTS users;
                       
                       CREATE TABLE users(
                           id   INTEGER PRIMARY KEY AUTOINCREMENT,
                           username TEXT UNIQUE,
                           city TEXT,
                           interests    TEXT     --comma separated, e.g. 'coding,music'
                           
                       );
                       
                       CREATE TABLE follows(
                           follower_id   INTERGER NOT NULL,
                           following_id  INTERGER NOT NULL,
                           PRIMARY KEY   (follower_id,following_id),
                           FOREIGN KEY   (follower_id) REFERENCES users(id),
                           FOREIGN KEY   (following_id) REFERENCES users(id),
                           CHECK    (follower_id != following_id)
                       );
                       CREATE INDEX idx_follower ON follows(follower_id);
                       CREATE INDEX idx_following ON follows(following_id);
                       """)
def generate_users(conn,n=60):
        rows=[]
        for i in range(n):
            username=f"{random.choice(FIRST_NAMES).lower()}{i}"
            city=random.choice(CITIES)
            interests=",".join(random.sample(INTERESTS,random.randint(2,4)))
            rows.append((username,city,interests))
        conn.executemany("INSERT INTO users(username,city,interests) VALUES(?,?,?)",rows)
        
def generate_follows(conn,min_follow=3,max_follow=12):
        """Users prefer following same_city/similar-intere.st users (more realistictic)."""
        users=conn.execute("SELECT id,city,interests FROM users").fetchall()
        edge=set()
        for uid,city,interests in users:
            my_interests=set(interests.split(","))
            weights=[]
            for vid,vcity,vint in users:
                if vid==uid:
                    weights.append(0)
                    continue
                w=1
                if vcity==city:
                    w+=3
                w+=2*len(my_interests & set(vint.split(",")))
                weights.append(w)
            count=random.randint(min_follow, max_follow)
            targets=random.choices([u[0] for u in users],weights=weights,k=count)
            for t in set(targets):
                if t!=uid:
                    edge.add((uid,t))
        conn.executemany(
            "INSERT INTO follows(follower_id,following_id) VALUES(?,?)",list(edge))
                    
            
def summary(conn):
    u=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    f=conn.execute("SELECT COUNT(*) FROM follows").fetchone()[0]
    print(f"Users:{u}|Follow edge:{f}")
    print("Sample users:")
    for row in conn.execute("SELECT username,city,interests FROM users LIMIT 5"):
        print(" ",row)
        
        
        
if __name__=="__main__":
    random.seed(42)
    conn=get_connection()
    create_tables(conn)
    generate_users(conn,n=60)
    generate_follows(conn)    
    conn.commit()
    summary(conn)
    conn.commit()
    