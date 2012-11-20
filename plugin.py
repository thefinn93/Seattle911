###
# Copyright (c) 2012, Finn Herzfeld
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.ircmsgs as ircmsgs
from supybot.i18n import PluginInternationalization, internationalizeDocstring

import supybot.schedule as schedule
import supybot.conf as conf
import requests
import json

_ = PluginInternationalization('SubredditAnnouncer')

@internationalizeDocstring
class SubredditAnnouncer(callbacks.Plugin):
    """Add the help for "@plugin help SubredditAnnouncer" here
    This should describe *how* to use this plugin."""
    pass
    
    def __init__(self, irc):
        self.__parent = super(SubredditAnnouncer, self)
        self.__parent.__init__(irc)
        self.savefile = conf.supybot.directories.data.dirize("subredditAnnouncer.db")
                
        def checkForPosts():
            self.checkReddit(irc)
        try:
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, 'redditCheck', False)
        except AssertionError:
            schedule.removeEvent('redditCheck')
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, 'redditCheck', False)
    
    def post(self, irc, channel, msg):
        try:
            irc.queueMsg(ircmsgs.privmsg(channel, unicode(msg)))
        except:
            print "Failed to send to channel"
    
    def checkReddit(self, irc):
        try:
            data = json.load(open(self.savefile))
        except Exception as inst:
            data = {"announced":[],"subreddits":[]}
        for channelsubreddit in self.registryValue('subreddits'):
            try:
                addtoindex = []
                channel = channelsubreddit.split(":")[0]
                sub = channelsubreddit.split(":")[1]
                listing = json.loads(requests.get(self.registryValue('domain') + "/r/" + sub + "/new.json?sort=new").content)
                for post in listing['data']['children']:
                    if not post['data']['id'] in data['announced']:
                        shortlink = chr(037) + self.registryValue('domain') + "/" + post['data']['id'] + chr(037)
                        if self.registryValue('shortdomain') != None:
                            shortlink = chr(037) + self.registryValue('shortdomain') + "/" + post['data']['id'] + chr(037)
                        
                        if post['data']['subreddit'] in data['subreddits']:
                            self.post(irc, channel, "[NEW] [/r/" + post['data']['subreddit'] + "] " + chr(002) + post['data']['title'] + chr(002) + " [" + chr(003) + "03" + str(post['data']['score']) + chr(017) + "] (" + chr(003) + "02" + str(post['data']['ups']) + chr(017) + "|" + chr(003) + "04" + str(post['data']['downs']) + chr(017) + ")  " + shortlink)
                        else:
                            if not post['data']['subreddit'] in addtoindex:
                                addtoindex.append(post['data']['subreddit'])
                        data['announced'].append(post['data']['id'])
            except:
                continue
            if not sub in data['subreddits']:
                data['subreddits'].extend(addtoindex)
        savefile = open(self.savefile, "w")
        savefile.write(json.dumps(data))
        savefile.close()
    
    def check(self, irc, msg, args):
        """takes no args
        
        Checks the specified subreddit and announces new posts"""
        self.checkReddit(irc)
    check = wrap(check)
    
    def start(self, irc, msg, args):
        """takes no arguments

        A command to start the node checker."""
        # don't forget to redefine the event wrapper
        def checkForPosts():
            self.checkReddit(irc)
        try:
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, 'redditCheck', False)
        except AssertionError:
            irc.reply('The reddit checker was already running!')
        else:
            irc.reply('Reddit checker started!')
    start = wrap(start)
    
    def stop(self, irc, msg, args):
        """takes no arguments

        A command to stop the node checker."""
        try:
            schedule.removeEvent('redditCheck')
        except KeyError:
            irc.reply('Error: the reddit checker wasn\'t running!')
        else:
            irc.reply('Reddit checker stopped.')
    stop = wrap(stop)

Class = SubredditAnnouncer


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
