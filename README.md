# cscq-salaries

The subreddit [/r/cscareerquestions](https://reddit.com/r/cscareerquestions)
hosts periodic 'salary sharing' threads, where software
engineers and interns are encouraged to share the fiscal 
details of their offers. However, much of the data in these
threads are obscured by inconsistent text formats and numerous
styling issues. This is an attempt to parse the rather varied data, 
sanitize it, and then convert it into easily readable, 
visually appealing figures.

## Installation Process 

After cloning this repository, `cd` in and setup a virtualenv.
```
virtualenv venv
source venv/bin/activate
```

Install all dependencies.
```
pip install -r requirements.txt
```

Provide an environment file (.env in the top level directory).
This environment file should have the following variables:
* `PRAW_CLIENT_ID` - [script OAuth application](https://github.com/reddit-archive/reddit/wiki/OAuth2) client ID 
* `PRAW_CLIENT_SECRET` - [script OAuth application](https://github.com/reddit-archive/reddit/wiki/OAuth2) client secret 
* `PRAW_USERNAME` - your reddit username 
* `PRAW_PASSWORD` - your reddit password 

Finally, run the appropriate file to generate salary data.
For internship salary data, use:
```
python cscqsal/interns.py
```
