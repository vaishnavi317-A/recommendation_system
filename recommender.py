import math 
from collections import defaultdict
from database import get_connection
def load_graph(conn):
    following=defaultdict(set)
    followers=defaultdict(set)
    for a,b in conn.execute("SELECT follower_id,following_id FROM follows"):
        following[a].add(b)
        followers[b].add(a)
    return following,followers
def load_users(conn):
    return{uid: (city,set(interests.split(",")))
           for uid,city,interests in conn.execute("SELECT id,city,interests FROM users")}
    
def recommend(uid,following,followers,users,top_n=5):
    candidates=set()
    for f in following[uid]:
        candidates |= following[f]
    candidates-=following[uid]
    candidates.discard(uid)
    
    
    my_city,my_int=users[uid]
    scored=[]
    for c in candidates:
        mutual=following[uid]&followers[c]
        aa=sum(1/math.log(max(len(followers[m])+len(following[m]),2))
            for m in mutual)
        c_city,c_int=users[c] 
        jac=len(my_int&c_int)/len(my_int|c_int)
        city_boost=1.0 if c_city==my_city else 0.0
        score=aa+0.5*jac+city_boost
        scored.append((c,round(score,3),len(mutual)))
    scored.sort(key=lambda x:x[1],reverse=True) 
    return scored[:top_n]
if __name__=="__main__":
    conn=get_connection()
    following,followers=load_graph(conn)
    users=load_users(conn)
    for uid in (1,2,3):
        print(f"User{uid}->",recommend(uid,following,followers,users))     
    