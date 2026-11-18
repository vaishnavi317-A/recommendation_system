import streamlit as st
import html

from database import get_connection
from recommender import load_graph, load_users, recommend

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="FriendFinder",
    page_icon="👥",
    layout="wide"
)

# ==========================================
# CUSTOM CSS
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #0b1020;
    color: white;
}

.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background-color: #171c2d;
}

.hero {
    background: linear-gradient(120deg, #312e81, #7c3aed);
    padding: 30px;
    border-radius: 18px;
    margin-bottom: 25px;
}

.hero h1 {
    color: white;
    font-size: 38px;
    margin: 0;
}

.hero p {
    color: #ddd6fe;
    font-size: 16px;
    margin-top: 10px;
}

.stat-card {
    background: #171f35;
    padding: 20px;
    border-radius: 14px;
    border: 1px solid #303b59;
}

.stat-number {
    color: #a78bfa;
    font-size: 28px;
    font-weight: bold;
}

.stat-label {
    color: #cbd5e1;
    font-size: 14px;
}

.friend-card {
    background: #171f35;
    border: 1px solid #303b59;
    border-radius: 16px;
    padding: 22px;
    margin-bottom: 15px;
}

.friend-card h3 {
    color: white;
    font-size: 21px;
    margin: 12px 0 8px 0;
}

.friend-card p {
    color: #cbd5e1;
    font-size: 14px;
    margin: 9px 0;
}

.avatar {
    background: linear-gradient(135deg, #7c3aed, #2563eb);
    width: 55px;
    height: 55px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 23px;
    font-weight: bold;
}

.badge {
    background: #312e81;
    color: #c4b5fd;
    padding: 6px 11px;
    border-radius: 20px;
    font-size: 12px;
    display: inline-block;
    margin: 4px 4px 4px 0;
}

hr {
    border-color: #303b59;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD DATABASE
# ==========================================

@st.cache_resource
def load_data():

    conn = get_connection()

    following, followers = load_graph(conn)

    users = load_users(conn)

    names = dict(
        conn.execute(
            "SELECT id, username FROM users"
        ).fetchall()
    )

    return following, followers, users, names

following, followers, users, names = load_data()

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title("👥 FriendFinder")

st.sidebar.caption("Discover New Connections")

st.sidebar.markdown("---")

uid = st.sidebar.selectbox(
    "Select User",
    options=list(names),
    format_func=lambda i: (
        f"{names[i]} ({users[i][0]})"
    )
)

k = st.sidebar.slider(
    "Number of Suggestions",
    min_value=3,
    max_value=10,
    value=5
)

st.sidebar.markdown("---")

st.sidebar.info(
    "Find people through mutual friends, "
    "shared interests and location."
)

# ==========================================
# HEADER
# ==========================================

st.html("""
<div class="hero">
    <h1>👥 FriendFinder</h1>
    <p>
        Discover people you may know.
        Build meaningful connections.
    </p>
</div>
""")

# ==========================================
# RECOMMENDATIONS
# ==========================================

suggestions = recommend(
    uid,
    following,
    followers,
    users,
    k
)

# ==========================================
# STATISTICS
# ==========================================

st.subheader("Your Network")

col1, col2, col3 = st.columns(3)

stats = [
    (len(users), "Total Users"),
    (len(following[uid]), "Following"),
    (len(suggestions), "Suggestions")
]

for col, (number, label) in zip(
    [col1, col2, col3], stats
):

    with col:

        st.html(f"""
        <div class="stat-card">
            <div class="stat-number">
                {number}
            </div>

            <div class="stat-label">
                {label}
            </div>
        </div>
        """)

# ==========================================
# ALREADY FOLLOWING
# ==========================================

st.markdown("---")

st.subheader("✓ Already Following")

already_following = [
    names[f]
    for f in following[uid]
    if f in names
]

if already_following:

    st.write(" · ".join(already_following))

else:

    st.info("You are not following anyone yet.")

# ==========================================
# SUGGESTED FRIENDS
# ==========================================

st.markdown("---")

st.subheader("✨ Suggested for You")

st.caption(
    "People selected by our recommendation algorithm"
)

if suggestions:

    for index, (c, score, mutual) in enumerate(suggestions):

        city, interests = users[c]

        username = html.escape(str(names[c]))

        city = html.escape(str(city))

        initial = html.escape(
            str(names[c])[0].upper()
        )

        # INTEREST TAGS

        interest_tags = ""

        for interest in sorted(interests):

            interest_tags += (
                f'<span class="badge">'
                f'{html.escape(str(interest))}'
                f'</span>'
            )

        # RECOMMENDATION SCORE

        try:
            score_text = f"{float(score):.3f}"

        except (ValueError, TypeError):
            score_text = html.escape(str(score))

        # FRIEND CARD

        st.html(f"""
        <div class="friend-card">

            <div class="avatar">
                {initial}
            </div>

            <h3>{username}</h3>

            <p>
                📍 {city}
            </p>

            <p>
                👥 Mutual Friends:
                <b>{mutual}</b>
            </p>

            <p>
                ⭐ Recommendation Score:
                <b>{score_text}</b>
            </p>

            <p>
                <b>Common Interests</b>
            </p>

            {interest_tags}

        </div>
        """)

else:

    st.info("No recommendations available.")

# ==========================================
# FOOTER
# ==========================================

st.markdown("---")

st.html("""
<div style="
    text-align: center;
    color: #94a3b8;
    padding: 15px;
">
    <b>FriendFinder</b>
    <br>
    Smart People Recommendation System
    <br>
    Built with Python and Streamlit
</div>
""")