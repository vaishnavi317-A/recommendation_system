import random
from collections import defaultdict
from recommender import recommend,load_users
from database import get_connection


def evaluate(k=5,hide_frac=0.2,seed=42):
    random.seed(seed)
    conn=get_connection()
    users=load_users(conn)
    edges=conn.execute("SELECT follower_id,following_id FROM follows").fetchall()
    
    
    by_user=defaultdict(list)
    for a,b in edges:
        by_user[a].append(b)
    
    
    hidden,following,followers={},defaultdict(set),defaultdict(set)
    for a,targets in by_user.items():
        random.shuffle(targets)
        n_test=max(1,int(len(targets)*hide_frac))
        hidden[a]=set(targets[:n_test])
        for t in targets[n_test:]:
            following[a].add(t)
            followers[t].add(a)
            
    all_ids=list(users)
    model_p,random_p=0,0
    for uid in hidden:
        recs=[c for c,_, _ in recommend(uid,following,followers,users,k)]
        model_p+=len(set(recs)&hidden[uid])/k
        rand=random.sample([u for u in all_ids if u!=uid],k)
        random_p+=len(set(rand)&hidden[uid])/k
        
    n=len(hidden)
    print(f"Precision@{k} (model): {model_p/n:.3f}")
    print(f"Precision@{k} (random): {random_p/n:.3f}")
    
    
    
if __name__=="__main__":
    evaluate()