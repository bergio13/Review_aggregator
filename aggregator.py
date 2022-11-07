import streamlit as st

import requests
from bs4 import BeautifulSoup
from rotten_tomatoes_scraper.rt_scraper import MovieScraper
import imdb
import mal

user_agent = {'User-agent': 'Mozilla/5.0'}

st.set_page_config(page_title='Review aggregator', page_icon=':anger:')

#-----HEADER SECTION
st.subheader('Review Aggregator - Movies/Tv shows/Animes')
st.title('Title:')
title = st.text_input(label='Insert title')
genre = st.radio('Choose the genre', ('Movie', 'Tv Show', 'Anime'))


#Metacritic
def search_meta(title, genre):
    # Genre can be 'tv' or 'movie'
    if genre == 'Movie':
        genre = 'movie'
    else:
        genre = 'tv'
    
    title = title.lower().replace(' ', '-').replace(':', '')
    meta_url = 'https://www.metacritic.com/' + genre + '/' + title
    meta = requests.get(meta_url, headers=user_agent)
    soup = BeautifulSoup(meta.text, 'html.parser')
    meta_critic_rev = float(soup.find('td', class_='summary_right').text) / 10
    meta_user_rev = soup.find('td', class_='summary_right pad_btm1').text
    if meta_user_rev != '\n\ntbd\n\n':
        meta_user_rev = float(meta_user_rev)
    else:
        meta_user_rev = 'No score yet'
        
    return meta_url, meta_critic_rev, meta_user_rev
        
#Rotten Tomatoes
def search_rt(title, genre):
    # Genre 'tv' or 'm'
    # Genre can be 'tv' or 'movie'
    if genre == 'Movie':
        genre = 'm'
    else:
        genre = 'tv'
    
    title = title.lower().replace(' ', '_').replace(':', '')
    rt_url = 'https://www.rottentomatoes.com/' + genre + '/' + title
    rt = requests.get(rt_url, headers=user_agent)
    soup = BeautifulSoup(rt.text, 'html.parser')
    if genre == 'tv':
        reviews = soup.findAll('span', class_='mop-ratings-wrap__percentage')
        rt_critic_rev = int(reviews[0].text.replace(' ', '').replace('\n', '').replace('%', '')) / 10
        rt_user_rev = int(reviews[1].text.replace(' ', '').replace('\n', '').replace('%', '')) / 10   
    else:
        movie_scraper = MovieScraper(movie_url=rt_url)
        movie_scraper.extract_metadata()
        reviews = movie_scraper.metadata
        rt_critic_rev = int(reviews['Score_Rotten']) / 10
        rt_user_rev = int(reviews['Score_Audience']) / 10
    
    return rt_url, rt_critic_rev, rt_user_rev

#IMDB
def search_imdb(title):
    ia = imdb.Cinemagoer()
    try:
        # Do the search, and get the results (a list of Movie objects).
        results = ia.search_movie(title)
    except imdb.IMDbError as e:
        print("Probably you're not connected to Internet.  Complete error report:")
        print(e)
        sys.exit(3)
    movie = ia.search_movie(title.lower())
    print(movie)
    imdb_id = movie[0].getID()
    imdb_url = 'https://imdb.com/title/tt' + imdb_id
    im = requests.get(imdb_url, headers=user_agent)
    soup = BeautifulSoup(im.text, 'html.parser')
    score = float(soup.find('span', class_='sc-7ab21ed2-1 jGRxWM').text)
    
    return imdb_url, score

#MAL
def search_mal(title):
    search = mal.AnimeSearch(title)
    
    return search.results[0].url, search.results[0].score


if title != '':
    try:
        rt = ' - '.join(str(i) for i in search_rt(title, genre))
    except:
        rt = 'Nothing found'
    try:
        imdb = ' - '.join(str(i) for i in search_imdb(title))
    except:
        imdb = 'Nothing found'
    try:
        mal = ' - '.join(str(i) for i in search_mal(title))
    except:
        mal = 'Nothing found'
    try:
        meta = ' - '.join(str(i) for i in search_meta(title, genre))
    except:
        meta = 'Nothing found'
    
                  
    st.markdown('### Rotten Tomatoes:')
    st.write(rt)
    st.markdown('### IMdB:')
    st.write(imdb)
    if genre == 'Anime':
        st.markdown('### My Anime List:')
        st.write(mal)
    else:
        st.markdown('### Metacritic:')
        st.write(meta)
        
        
        
