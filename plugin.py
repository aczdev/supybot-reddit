###
# Supybot-reddit ~ a quick and dirty plugin to display the newest or the hottest
# entries from Reddit.com subreddits. Written to have some fun with testing PRAW
# library in Python.
# Copyright (c) 2016, Adam Cz.
#
# TODO list:
# [x] do exceptions for a wrong subreddit
# [ ] format the text
# [ ] add more options?
#
###

import praw
from praw.errors import InvalidSubreddit, Forbidden

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Reddit')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x

# Colourses :)
RED = '\x0304'
ORANGE = '\x0307'
YELLOW = '\x0308'
GREEN = '\x0309'
PINK = '\x0313'
BROWN = '\x0305'
PURPLE = '\x0306'
WHITE = '\x0300'
BLUE = '\x0311'
BOLD = '\x02'
RA = '\x0F'
NA = RED + 'N/A' + RA


class Reddit(callbacks.Plugin):
    """Plugin allows IRC channel users to search the latest submissions on 
    Reddit.com subreddits like /r/pics and /r/cars"""
    threaded = True

    def display(self, title, score, url, nsfw, author):
        reply = ''
        if nsfw:
            reply = '[' + RED + BOLD + '+18' + RA + '] '
        reply +=    title + ' | ' + 'Points: ' + str(score) + ' | ' + \
                    'Author: ' + str(author) + ' | ' + 'Link: ' + url
        return reply

    def r(self, irc, msg, args, subreddit, status, period, n=1):
        """<subreddit> <top/hot/new/rising/controversial>
        <hour/day/week/month/year/all> <links count>
        """

        # Just a bit of history to include some fun to Reddit statistics :)
        user_agent = 'Lynx/2.8.5rel.2 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/0.9.7d'
        reddit = praw.Reddit(user_agent=user_agent)
        sub = reddit.get_subreddit(subreddit)

        if not n:
            n = 1
        #    try:
        #        n = int(period) 
        #    except (TypeError, ValueError):
        #        n = 3
        #if not period:
        #    period='day'

        irc.reply('subreddit=%s, status=%s, period=%s, n=%s' % \
                            (type(subreddit), type(status), type(period), type(n)))

        #if int(n) > 10:
        #    irc.reply('%d? Do not go so crazy, man!' % n)
        #    return None

        #try:
        #    if int(n):
        #        n = n
        #except (TypeError, ValueError):
        #    try:
        #        irc.reply('Looking for an int in period!')
        #        if int(period):
        #            n = period
        #            period = 'day'
        #    except (TypeError, ValueError):
        #        try:
        #            irc.reply('Looking for an int in status')
        #            if int(status):
        #                n = status
        #                status = 'top'
        #                period = 'day'
        #        except (TypeError, ValueError):
        #            irc.reply('No ints? Go default way!')
        #            n = 1
        #            period = 'day'
        #            status = 'top'

        try:
            if status == 'hot':
                result = sub.get_hot(limit=n)
            elif status == 'new':
                result = sub.get_new(limit=n)
            elif status == 'rising':
                result = sub.get_rising(limit=n)
            elif status == 'top':
                try:
                    func = getattr(sub, 'get_top_from_' + period)
                    result = func(limit=n)
                except (AttributeError, TypeError):
                    result = sub.get_top(limit=n)
            elif status == 'controversial':
                try:
                    func = getattr(sub, 'get_controversial_from_' + period)
                    result = func(limit=n)
                except (AttributeError, TypeError):
                    result = sub.get_controversial(limit=n)
            else:
                irc.reply(RED + BOLD + 'Choice error: ' + RA + 'top/hot/new/rising/controversial')
                return None

            title = BLUE + BOLD + 'Reddit.com/r/' + ORANGE + subreddit + RA
            irc.reply(title)
            try:
                for sm in result:
                    irc.reply(self.display(sm.title, sm.score, sm.url, sm.over_18, sm.author))
            except TypeError:
                irc.error('Something went wrong. Posting random stuff!')
                result = sub.get_random_submission()
                irc.reply(self.display(result.title, result.score, result.url, result.over_18, result.author))

        except (InvalidSubreddit, Forbidden) as e:
            if str(e) == 'HTTP error':
                irc.reply('This subreddit is private')
            elif str(e) == 'SUBREDDIT_NOEXIST':
                irc.reply('There is no such subreddit')
            return None
    r = wrap(r, ['somethingWithoutSpaces', 'somethingWithoutSpaces', 'somethingWithoutSpaces', optional('int')])


Class = Reddit


