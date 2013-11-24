This plugin checks a list of Seattle area 911 calls and announces them in IRC as they come in.

Install the plugin, then enable it in a channel by setting the channel configuration varible
`supybot.plugins.Seattle911.enable` to `on`.

The "format" option dictates how the bot should announce messages to the
channel. You can also specify a `[global]` section with a default format.
Available options are:
 
* `{address}` - The address that the incident occured at.

* `{longitude}` - The longitude that the incident occured at.

* `{latitude}` - The latitude that the incident occured at.

* `{incident_number}` - A unique identifier assigned to the incident.

* `{incident_type}` - the type of incident. For example, "Aid Response", "Medic Response", "Auto Fire Alarm"

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
