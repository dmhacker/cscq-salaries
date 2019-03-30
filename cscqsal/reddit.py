from dotenv import load_dotenv

import praw
import os

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

reddit = praw.Reddit(client_id=os.getenv('PRAW_CLIENT_ID'),
                     client_secret=os.getenv('PRAW_CLIENT_SECRET'),
                     username=os.getenv('PRAW_USERNAME'),
                     password=os.getenv('PRAW_PASSWORD'),
                     user_agent="/r/cscareerquestions analytics "
                                "script created by /u/dmhacker")
