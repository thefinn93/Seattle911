This plugin checks a list of subreddits for new posts and announces them in IRC as they come in.

Install the plugin, then configure edit the config file ( `Seattle911
.ini` in the data directory) in this format:

```ini
[#channel]
subreddits = all
domain = http://www.uppit.us
shortdomain = http://uppit.us
redditname = uppit

[#netsec]
subreddits = netsec
format = [NEW] [{redditname}] [/r/{subreddit}] {bold}{title}{bold} - {shortlink}
```

The "format" option dictates how the bot should announce messages to the
channel. You can also specify a `[global]` section with a default format.
If none is specificed, the one shown above is used. Available options are:
 
* `{redditname}` - the name of the reddit site. Usually Reddit, but clones
exist

* `{subreddit}` - the name of the subreddit, not including the /r/

* `{title}` - the title of the post

* `{author}` - the user who posted it

* `{link}` - the link that was submitted. For selfposts, this is the long form URL to the comments

* `{shorturl}` - the redd.it short URL

* `{score}` - the current score of the post

* `{ups}` - the number of upvotes it's received

* `{downs}` - the number of downvotes it's received

* `{comments}` - the number of comments it's received

* `{domain}` - the domain of the URL of the post (self.subreddit for selfposts)

* `{bold}` - the code to start or stop bold formatting

* `{underline}` - underline the enclosed text

* `{reverse}` - reverse or italicize the enclosed text (some clients inverse the colors, other italicize)

* `{white}` - make the enclosed text white

* `{black}` - make the enclosed text black

* `{blue}` - make the enclosed text blue

* `{red}` - make the enclosed text red

* `{dred}` - make the enclosed text dark red

* `{purple}` - make the enclosed text purple

* `{lpurple}` - light purple

* `{yellow}` - make the enclosed text yellow

* `{dyellow}` - make the enclosed text dark purple

* `{green}` - make the enclosed text green

* `{lgreen}` - make the enclosed text light green

* `{dgreen}` - make the enclosed text dark green

* `{lgrey}` - make the enclosed text light grey

* `{dgrey}` - make the enclosed text dark grey

* `{close}` - resets the color

Feel free to request additional fields.

Pull requests, bugreports, etc are always welcome.
