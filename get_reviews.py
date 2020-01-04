import bs4
import requests
import datetime
import textwrap
import random
import sqlite3
from profanityfilter import ProfanityFilter


def main():
    review_list = getReviews()
    conn = sqlite3.connect('reviews.db')
    c = conn.cursor()
    for review in review_list:
        #string = 'INSERT OR REPLACE INTO reviews VALUES (\"%s\", \"%s\", %d, \"%s\");' % (str(review.timestamp), str(review.title), review.stars, str(review.body))
       # c.execute(string)
        c.execute("INSERT OR REPLACE INTO reviews VALUES (?, ?, ?, ?);", (str(review.timestamp), str(review.title), review.stars, str(review.body)))
    conn.commit()
    conn.close()

class Review:
    def __init__(self, timestamp, title, stars, body):
        self.timestamp = timestamp
        self.title = title
        self.stars = stars
        self.body = body
        self.photo = 'reviews/' + str(self.timestamp)+' ' + str(self.title) + '.png'

    def __repr__(self):
        string = str(self.timestamp) + ' | ' + str(self.title) + ' | ' + str(self.stars) + ' | ' + str(self.body)[:20] + '...'
        return string

def getReviews():
    # Get the HTML of the page, and parse it
    r = requests.get('https://www.edmovieguide.com/recentreviews/4')
    data = r.text
    soup = bs4.BeautifulSoup(data, "lxml")
    pf  = ProfanityFilter()
    # We retrieve all the reviews based on their tag
    reviews = soup.find_all("div", {"class":"recent-reviews"})
    review_list = []
    for review in reviews:
        stars = 0
        title = ''
        body = ''
        timestamp = ''
        parts = []
        for thing in review:
            if isinstance(thing, bs4.element.Tag):
                for i in thing: 
                    if isinstance(i, bs4.element.Tag):
                        if str(i) == "<span class=\"star fullStar\"></span>":
                            # The user has given the movie a star, so we increment the counter
                            stars += 1
                    else:
                        if len(str(i)) == 1:
                            pass
                        else:
                            parts.append(i)
        title = parts[0]
        timestamp = parts[1] + ' ' + str(datetime.datetime.now().year)
        body = parts[2]
        new_review = Review(timestamp, title, stars, body)
        # Adding some custom profanities cause people suck
        pf.extra_profane_word_dictionaries = {'en': {'trans', 'transgender', 'tranny', 'SJW'}}
        if pf.is_clean(str(body)):
            review_list.append(new_review)
    return review_list

if __name__ == "__main__":
    main()