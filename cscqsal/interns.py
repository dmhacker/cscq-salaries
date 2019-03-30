from reddit import reddit
from companies import COMPANIES

import pprint
import sys

companies = {} 

for submission in reddit.subreddit('cscareerquestions') \
        .search('Salary Sharing thread intern'):
    if '[OFFICIAL] Salary Sharing thread' not in submission.title:
        continue
    print("Collecting comments from '{0}'.".format(submission.title))
    submission.comments.replace_more(limit=0, threshold=0)
    for region_comment in submission.comments:
        region = region_comment.body
        if 'Region -' not in region or 'US' not in region:
            continue
        for comment in region_comment.replies:
            content = comment.body \
                .lower() \
                .replace(' /', '/') \
                .replace('/ ', '/')

            header_tags = ['prior experience', 'previous experience', 'school']

            for tag in header_tags:
                header_idx = content.find(tag)
                if header_idx >= 0:
                    header_idx += len(tag)
                    content = content[header_idx:]
                    end_header_idx = content.find('\n')
                    content = content[end_header_idx:]

            for company in COMPANIES:
                company_idx = content.find(company.lower())
                if company_idx >= 0:
                    salary = -1
                    for i in range(company_idx, len(content)):
                        if content[i] == '/' and \
                                (content[i - 1].isnumeric() or
                                 content[i - 1] == 'k') and \
                                content[i + 1] in 'hmw':
                            end = i
                            start = i - 1
                            while start >= 0 and \
                                    (content[start].isnumeric() or
                                     content[start] == '.' or
                                     content[start] == ',' or
                                     (content[start] == 'k' and
                                      start == i - 1)):
                                start -= 1
                            start += 1
                            salary = float(content[start:end]
                                           .replace(',', '')
                                           .replace('k', ''))
                            if content[i - 1] == 'k':
                                salary *= 1000
                            if content[i + 1] == 'h':
                                salary *= 160
                            if content[i + 1] == 'w':
                                salary *= 4
                            if salary < 1000 or salary > 20000:
                                print("Skipping #{0} ({1}). "
                                      "Salary is ${2}/month?"
                                      .format(comment.id, company, salary))
                                salary = -1
                                break
                            # print("{0}: {1}".format(company, salary))
                            break
                    if salary > 0:
                        salary /= 160
                        if company not in companies:
                            companies[company] = [0, 0]
                        stats = companies[company]
                        [avg, cnt] = stats
                        stats[0] = ((avg * cnt) + salary) / (cnt + 1)
                        stats[1] += 1

pprint.pprint(companies)
