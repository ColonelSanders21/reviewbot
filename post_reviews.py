import tweepy
import glob
import os
import get_reviews
import get_auth
import textwrap
import io
import random
import time
import sqlite3
import base64
from PIL import Image, ImageDraw, ImageFont
from get_reviews import Review

def main():
    while True:

        # Authenticate to Twitter
        zeroAuth = get_auth.getZeroAuth()
        accessTokens = get_auth.getAccessTokens()
        auth = tweepy.OAuthHandler(zeroAuth[0], zeroAuth[1])
        auth.set_access_token(accessTokens[0], accessTokens[1])

        # Create API object
        api = tweepy.API(auth)
        get_reviews.main()
        # Connect to the db
        conn = sqlite3.connect('reviews.db')
        c = conn.cursor()

        # Get one review
        
        query = 'select *  from reviews ORDER BY RANDOM() limit 1;'
        c.execute(query)
        review_row = c.fetchone()
        if review_row != None:
            # Create a review object
            review = Review(review_row[0], review_row[1], review_row[2], review_row[3])
            
            # Generate the image
            image_filename = generateImage(review)

            # Create a tweet
            media_ids = []
            image = api.media_upload(filename = image_filename)
            media_ids.append(image.media_id)
            stars = '⭐' * int(review.stars)
            api.update_status(status=review.title + ':\n' + stars, media_ids = media_ids)

            # And now we mark the tweet as having been tweeted so we can avoid tweeting it again
            print('Posted ' + review.title + ' ' + review.timestamp)

            # Add review to our DB so it can't get posted again
            query = 'INSERT INTO posted VALUES(\"%s\", \"%s\");' % (str(review.timestamp) , str(review.title))
            c.execute(query)
            conn.commit()
            conn.close()
            # Delete the temp image
            os.remove(image_filename)
        # Hush. It's time to sleep.
        print("Going into sleep mode.\n")
        max_time = 30
        time_elapsed = 0
        while time_elapsed != max_time:
            #if time_elapsed == 30:
                # We scrape every 30 mins, and we post every 60.
                #get_reviews.main()
                #print('Got reviews.\n')
            print('Next post: ' + str(max_time-time_elapsed) + ' minutes.\n')
            time.sleep(300)
            time_elapsed += 5

def generateImage(review):
    review_length = len(review.body)
    # Choose a random color -- from 1 to 4
    color = random.randint(1,4)
    img = Image.open(str(color) +'.jpg')
    MAX_W, MAX_H = img.size
    # Following is based on handmade testing. Let's see how this goes.
    if review_length <= 600:
        font_size = 20
        cpl = 39
    elif review_length > 600 and review_length <= 864:
        font_size = 18
        cpl = 48
    elif review_length > 864 and review_length <= 1160:
        font_size = 16
        cpl = 58
    else:
        font_size = 14
        cpl = 60
    text = textwrap.wrap(review.body)
    fnt = ImageFont.truetype("/usr/share/fonts/dejavu/DejaVuSans.ttf",font_size)
    d = ImageDraw.Draw(img)
    # We need to sort out what the height of our text is
    line_dimensions = [d.textsize(line, font=fnt) for line in text]
    offset = (MAX_H - sum(h for w, h in line_dimensions)) // 2
    current_h = offset - 60
    for line, (w, h) in zip(text, line_dimensions):
        d.text(((MAX_W - w) // 2, current_h), line, font=fnt, fill="black")
        current_h += h
    filename = "temp.jpg"
    img.save(filename)
    return(filename)

if __name__ == "__main__":
    main()