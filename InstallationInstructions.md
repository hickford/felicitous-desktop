## Dependencies ##
  * A desktop - Windows or Linux/GNOME (XFCE and KDE are lost somewhere)
  * Python 2.x
  * PyEphem
  * flickrapi
  * [PIL](http://www.pythonware.com/products/pil/) (only necessary on Windows)

The Python modules can both be installed using [Pip](http://pypi.python.org/pypi/pip) as follows
```
pip install pyephem
pip install flickrapi
pip install PIL
```


Or you can install the Python modules with [setuptools](http://pypi.python.org/pypi/setuptools), as follows:
```
easy_install pyephem
easy_install flickrapi
easy_install PIL
```

## Installation ##

Download the code (clone the repository or [download this](http://felicitous-desktop.googlecode.com/hg/felicitous.py)) and place the Python script felicitous.py anywhere, perhaps ~/bin .

## Usage ##

felicitous.py - no options are necessary

```
Usage: felicitous.py [options]

Set an interesting desktop background from flickr based on time of day and
current weather for your location.

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  -l YAHOO_LOCATION_PARAMETER, --location=YAHOO_LOCATION_PARAMETER
                        Yahoo weather location parameter
  -w WEATHER, --weather=WEATHER
                        force weather
  -t TIME_OF_DAY, --time-of-day=TIME_OF_DAY
                        force time of day
  -n, --nilpotent       don't download anything, just print URLs
```

## Files ##

The script will download and save the backgrounds to ~/felicitous

## cronjob ##

Run the script hourly

```
0 * * * * ~/bin/felicitous.py -l UKXX0028
```

where XXXXXX is the Yahoo weather code for your approximate location. You can determine it [with ease](http://www.edg3.co.uk/snippets/weather-location-codes/) or on [Yahoo Weather](http://weather.yahoo.com/) itself, inspecting the URL of the RSS feed for your location.