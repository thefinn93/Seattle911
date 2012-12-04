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
import ConfigParser
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
        self.headers = {"User-Agent":"SubredditAnnouncer (thefinn93@thefinn93.com)"}
                
        def checkForPosts():
            self.checkReddit(irc)
        try:
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, 'redditCheck', False)
        except AssertionError:
            schedule.removeEvent('redditCheck')
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, 'redditCheck', False)
    
    def post(self, irc, channel, msg):
        try:
            irc.queueMsg(ircmsgs.privmsg(channel, str(msg)))
        except Exception as e:
            self.log.warning("Failed to send to " + channel + ": " + str(type(e)))
            self.log.warning(str(e.args))
            self.log.warning(str(e))
    
    def checkReddit(self, irc):
        try:
            data = json.load(open(self.savefile))
        except Exception as inst:
            domain = "http://www.reddit.com"
            if self.registryValue('domain') is not "":
                doman = self.registryValue('domain')
            data = {domain: {"announced":[],"subreddits":[]}}
            
        parser = ConfigParser.SafeConfigParser()
        parser.read([self.registryValue('configfile')])
        for channel in parser.sections():
            try:
                addtoindex = []
                sub = parser.get(channel, 'subreddits')
                domain = self.registryValue('domain')
                if parser.has_option(channel, 'domain'):
                    domain = parser.get(channel, 'domain')
                if not domain in data:
                    data[domain] = {"announced":[],"subreddits":[]}
                self.log.info("Creating data store for " + domain)
                url = domain + "/r/" + sub + "/new.json?sort=new"
                self.log.info("Checking " + url + " for " + channel)
                request = requests.get(url, headers=self.headers)
                listing = json.loads(request.content)
                for post in listing['data']['children']:
                    if not post['data']['id'] in data[domain]['announced']:
                        shortlink = chr(037) + self.registryValue('domain') + "/" + post['data']['id'] + chr(037)
                        
                        if self.registryValue('shortdomain') != None:
                            shortlink = chr(037) + self.registryValue('shortdomain') + "/" + post['data']['id'] + chr(037)
                            
                        if parser.has_option(channel, 'shortdomain'):
                            shortlink = chr(037) + parser.get(channel, 'shortdomain') + "/" + post['data']['id'] + chr(037)
                        
                        redditname = ""
                        if self.registryValue('redditname') is not "":
                            redditname = " [" + self.registryValue('redditname') + "]"
                            self.log.info("Setting redditname to " + redditname + " because it's in the config")
                            
                        if parser.has_option(channel, 'redditname'):
                            redditname = " [" + parser.get(channel, 'redditname') + "] "
                            self.log.info("It appears that this channels uses a different reddit. Setting redditname to " + redditname)
                            
                        if post['data']['subreddit'] in data[domain]['subreddits']:
                            msg = "[NEW]" + redditname + " [/r/" + post['data']['subreddit'] + "] " + chr(002) + post['data']['title'] + chr(002) + " [" + chr(003) + "03" + str(post['data']['score']) + chr(017) + "] (" + chr(003) + "02" + str(post['data']['ups']) + chr(017) + "|" + chr(003) + "04" + str(post['data']['downs']) + chr(017) + ")  " + shortlink
                            self.log.info(msg)
                            self.post(irc, channel, msg)
                        else:
                            self.log.info("Not posting " + self.registryValue('shortdomain') + "/" + post['data']['id'] + " because it's our first time looking at /r/" + post['data']['subreddit'])
                            if not post['data']['subreddit'] in addtoindex:
                                addtoindex.append(post['data']['subreddit'])
                        data[domain]['announced'].append(post['data']['id'])
            except Exception as e:
                self.log.warning("Whoops! Something fucked up: " + str(e))
            if not domain in data:
                data[domain] = {"announced":[],"subreddits":[]}
                self.log.info("Creating data store for " + domain)
            if not sub in data[domain]['subreddits']:
                data[domain]['subreddits'].extend(addtoindex)
        savefile = open(self.savefile, "w")
        savefile.write(json.dumps(data))
        savefile.close()
    
    def check(self, irc, msg, args):
        """takes no args
        
        Checks the specified subreddit and announces new posts"""
        irc.reply("Checking!")
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
