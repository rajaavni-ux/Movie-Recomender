import streamlit as st
import pickle
import pandas as pd
import requests
import time

# 1. Configuration & API Key
API_KEY = "8b76b021cf092e79315626639acb7c0d"

# 2. Function to fetch posters from TMDB API
def get_movie_poster(movie_id):
    time.sleep(0.1) # Rate limiting se bachne ke liye
    
    # 1. Standard TMDB ID method
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    # 2. 'Find' method (IMDb IDs starting with 'tt' ke liye)
    find_url = f"https://api.themoviedb.org/3/find/{movie_id}?api_key={API_KEY}&external_source=imdb_id"
    
    try:
        # Agar ID 'tt' se start ho raha hai toh find_url use hoga
        if str(movie_id).startswith('tt'):
            response = requests.get(find_url, timeout=5)
            data = response.json()
            if data.get('movie_results'):
                path = data['movie_results'][0].get('poster_path')
                if path:
                    return "https://image.tmdb.org/t/p/w500/" + path
        else:
            # Normal numerical ID search
            response = requests.get(movie_url, timeout=5)
            data = response.json()
            path = data.get('poster_path')
            if path:
                return "https://image.tmdb.org/t/p/w500/" + path
                
        return "https://via.placeholder.com/500x750?text=No+Poster"
    except:
        return "https://via.placeholder.com/500x750?text=API+Error"

# 3. Recommendation Logic
def recommend(movie):
    # User ki selected movie ka index find karna
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    
    # Top 5 similar movies filter karna
    recommended_list = sorted(list(enumerate(distances)),
                              reverse=True,
                              key=lambda x: x[1])[1:6]

    recommended_names = []
    recommended_posters = []
    
    for i in recommended_list:
        # 'movie_id' ya 'id' dono ko check karna
        try:
            movie_id = movies.iloc[i[0]]['id']
        except KeyError:
            movie_id = movies.iloc[i[0]]['movie_id']

        recommended_names.append(movies.iloc[i[0]]['title'])
        recommended_posters.append(get_movie_poster(movie_id))

    return recommended_names, recommended_posters

# 4. Loading Data (Cached for performance)
@st.cache_resource
def load_data():
    try:
        # Pickle files ko load karna
        movies_dict = pickle.load(open("movies_list.pkl", "rb"))
        similarity = pickle.load(open("similarity.pkl", "rb"))
        movies = pd.DataFrame(movies_dict)
        return movies, similarity
    except FileNotFoundError:
        # Agar files missing hain toh error dikhana
        st.error("Pickle files not found! Check your folder.")
        return None, None

movies, similarity = load_data()

# 5. UI Layout
st.set_page_config(page_title="Netflix AI Recommender", layout="wide")
st.header("🎬 Movies Recommender System")

if movies is not None:
    movies_list = movies['title'].values
    selected_movie = st.selectbox("Select a movie:", movies_list)

    if st.button("Show Recommendation"):
        names, posters = recommend(selected_movie)
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                st.image(posters[i])
                st.caption(names[i])