###
# Copyright (c) 2014, Finn Herzfeld
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
import supybot.ircdb as ircdb
from supybot.i18n import PluginInternationalization, internationalizeDocstring

import supybot.schedule as schedule
import supybot.conf as conf
import requests
import ConfigParser
import json
from bs4 import BeautifulSoup
import re

_ = PluginInternationalization('Seattle911')

@internationalizeDocstring
class Seattle911(callbacks.Plugin):
    """No user interaction needed. Set the config
    as described in the README."""
    pass
    
    def __init__(self, irc):
        self.__parent = super(Seattle911, self)
        self.__parent.__init__(irc)
        self.savefile = conf.supybot.directories.data.dirize("Seattle911.db")
                
        def checkForPosts():
            self.checkForIncidents(irc)
        try:
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, '911check', False)
        except AssertionError:
            schedule.removeEvent('911check')
            schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, '911check', False)
    def post(self, irc, channel, msg):
        try:
            irc.queueMsg(ircmsgs.privmsg(channel, str(msg)))
        except Exception as e:
            self.log.warning("Failed to send to " + channel + ": " + str(type(e)))
            self.log.warning(str(e.args))
            self.log.warning(str(e))
    
    def checkForIncidents(self, irc):
        try:
            data = json.load(open(self.savefile))
        except Exception as inst:
            data = []
            
        soup = BeautifulSoup(requests.get("https://www2.ci.seattle.wa.us/fire/realtime911/getRecsForDatePub.asp?action=Today&incDate=&rad1=des").content)
        rows = soup.find_all("table")[3].find_all("tr")
        incidents = []
        for row in rows:
            try:
                tds = row.find_all("td")
                a = {}
                if len(tds[0].contents) > 0:
                    a['date'] = tds[0].contents[0]
                else:
                    a['date'] = "Unknown"
                    self.log.warning("Date missing!")
                if len(tds[1].contents) > 0:
                    a['number'] = tds[1].contents[0]
                else:
                    a['number'] = "Unknown"
                    self.log.warning("Incident number missing!")
                if len(tds[2].contents) > 0:
                    a['level'] = tds[2].contents[0]
                else:
                    a['level'] = "Unknown"
                    self.log.warning("Level missing for incident %s" % a['number'])
                if len(tds[3].contents) > 0:
                    a['units'] = tds[3].contents[0]
                else:
                    a['units'] = "Unknown"
                    self.log.warning("Units missing for incident %s" % a['number'])
                if len(tds[4].contents) > 0:
                    a['location'] = tds[4].contents[0]
                else:
                    a['location'] = "Unknown"
                    self.log.warning("Location missing for incident %s" % a['number'])
                if len(tds[5].contents) > 0:
                    a['type'] = tds[5].contents[0]
                else:
                    a['type'] = "Unknown"
                    self.log.warning("Type missing for incident %s" % a['number'])
                incidents.append(a)
            except IndexError:
                self.log.info(row.prettify())
            
        messageformat = "[911] [{number}][{type}] {location}"
        if self.registryValue('postformat'):
            messageformat = self.registryValue('postformat')
        actuallyannounce = True
        if len(data) == 0:
            actuallyannounce = False
        for incident in incidents:
            #self.log.info(incident)
            if not incident['number'] in data:
                msg = messageformat.format(
                    date = incident['date'],
                    number = incident['number'],
                    level = incident['level'],
                    units = incident['units'],
                    location = incident['location'],
                    type = incident['type'],
                    bold = chr(002),
                    underline = "\037",
                    reverse = "\026",
                    white = "\0030",
                    black = "\0031",
                    blue = "\0032",
                    red = "\0034",
                    dred = "\0035",
                    purple = "\0036",
                    dyellow = "\0037",
                    yellow = "\0038",
                    lgreen = "\0039",
                    dgreen = "\00310",
                    green = "\00311",
                    lpurple = "\00313",
                    dgrey = "\00314",
                    lgrey = "\00315",
                    close = "\003")
                for channel in irc.state.channels:
                    if self.registryValue('enabled', channel) and actuallyannounce:
                        self.post(irc, channel, msg)
                    else:
                        self.log.info("Not posting to %s: %s" % (channel, msg))
                data.append(incident['number'])
        #except Exception as e:
        #    self.log.warning("Whoops! Something fucked up! ")
        #    self.log.warning(str(type(e)))
        #    self.log.warning(str(e.args))
        #    self.log.warning(str(e))
        savefile = open(self.savefile, "w")
        savefile.write(json.dumps(data))
        savefile.close()
    
    def check(self, irc, msg, args):
        """takes no args
                
        Checks for new 911 calls"""
        if ircdb.checkCapability(msg.prefix, "owner"):
            irc.reply("Checking!")
            self.checkForIncidents(irc)
        else:
            irc.reply("Fuck off you unauthorized piece of shit")
    check = wrap(check)
    
    def start(self, irc, msg, args):
        """takes no arguments

        A command to start the node checker."""
        # don't forget to redefine the event wrapper
        if ircdb.checkCapability(msg.prefix, "owner"):
            def checkForPosts():
                self.checkForIncidents(irc)
            try:
                schedule.addPeriodicEvent(checkForPosts, self.registryValue('checkinterval')*60, '911check', False)
            except AssertionError:
                irc.reply('The 911 checker was already running!')
            else:
                irc.reply('911 checker started!')
        else:
            irc.reply("Fuck off you unauthorized piece of shit")
    start = wrap(start)
    
    def stop(self, irc, msg, args):
        """takes no arguments

        A command to stop the node checker."""
        if ircdb.checkCapability(msg.prefix, "owner"):
            try:
                schedule.removeEvent('911check')
            except KeyError:
                irc.reply('Error: the 911 checker wasn\'t running!')
            else:
                irc.reply('911 checker stopped.')
        else:
            irc.reply("Fuck off you unauthorized piece of shit")
    stop = wrap(stop)

Class = Seattle911


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
