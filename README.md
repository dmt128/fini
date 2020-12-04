# Fini

Fini is a python command line application that allows the user to gather company financial information from data available in the public domain. In particular the user can input one or more ticker symbols (e.g. AAPL, MSFT, AMZN etc) and the application will try and gather as much available public information as possible, about these companies, from websites such as zacks, finviz, yahoo finances, nasdaq, marketbeat, earningswhispers etc. The application can store this information for revisiting at a later time, to perform further analysis or even perform some basic historical analysis.

## Quick Start
Fini is a python module and it can run on any platform tha has at least Python 3.8 available. The use of a virtual environemnt is highly recommended but not mandatory. To install and use the module, do the following:

* ```git clone https://github.com/dmt128/fini.git```
* ```cd fini```
* ```python3 setup.py install```
* ```cd ~```
* ```fini```  

To uninstall the application, do the following:
* ```pip3 uninstall fini```

[NOTE] The command above uses `python3` and `pip3` but if you are working from within a virtual environment you should be able to use `python` and `pip` instead. You need to make sure that at least python v3.8 and pip3 are being invoked in either case.

## Usage
Once fini starts, you will see a welcome message and the prompt `Fini >> `, waiting for some user input. Any output is color coded in order to make viewing easier for the user. For example the prompt `Fini >> ` is always black text on white background, whereas the help info appears with green text on black background.

At this stage you can type `-h` or `--help` to see the help section with available commands and brief descriptions on their usage. What follows are detailed descriptions of all available commands and options.

### TICKER
The normal mode of operation is the TICKER positional argument. Anything you write at the prompt is treated as a ticker symbol, or a list of ticker symbols separated by space which are parsed one by one and produce any found financial information. For example if you type AMD at the prompt and press enter, the application will try to access all providers, it will gather any publicly available information on the company and display that to the screen. 
* `Fini >> AMD`
OR:
* `Fini >> AMD QCOM TSN` will display information for all three companies.

By default the application will visit all information providers but you can select a subset of those by enabling specific options at the command prompt after the ticker symbols. For example the following will gather information about AMD only from the zacks.com website (note that `Fini>> ` is the prompt, you don't need to write that):

* `Fini >> AMD --zacks`
OR 
* `Fini >> AMD AAPL --zacks` will display information for both companies but only from the zacks.com site.

### -h, --help
This command displays a help message that contains all available command and options along with brief descriptions on the usage.

### --version
This will display the current version of the application

### -v, --verbose
This command sets the verbosity level of the output.

### -s [display [set ...]], --settings [display [set ...]]
This command deals with the settings of the application. The -s/--settings command can perform multiple actions and has extra options. That is the user has to supply additional options after the -s/--settings command. The -s command supports the following options:

**d**, **dis** or **display**:
This option will display the current settings. All variations of the display command  (d, dis and display) do the same thing. The two first variations ('d' and 'dis') are provided to the user as shortcuts. For example the following commands do the same thing, they just display the state of the current settings:
* `Fini >> -s display`
* `Fini >> -s dis`
* `Fini >> -s d`
* `Fini >> --settings display`
* `Fini >> --settings dis`
* `Fini >> --settings d`

**s**, **set**:
This option allows the user to update a particular setting. The user needs to enter the key and value of the settings after the options. For example:

`Fini >> -s set stock_update_period_sec 500`

In the above command, the `-s` is the settings command, the `set` part is the option that tells the application to set/update a setting, the `stock_update_period_sec` is the key, that is the actual setting that we want to update and the `500` part is the new value we want to set.

In a similar fashion to the display options the following commands do the same thing:
* `Fini >> -s s stock_update_period_sec 500` 
* `Fini >> -s set stock_update_period_sec 500` 
* `Fini >> --settings s stock_update_period_sec 500` 
* `Fini >> --settings set stock_update_period_sec 500` 

### -t [list [TERM ...]], --term [list [TERM ...]]
This command allows the user to view the definitions and other aspects of terms that are routinely used during fundamental and technical analysis of a company. Although this information is readily and freely available in the public domain, this feature allows the user to quickly view the description of a term without the need to leave the application and go to a broswer. This feature is also very usefull for people who are new to investing.

This command performs multiple actions, and has the following options:

**list**
This option will display all available terms such as EPS, PE etc. For example the following will show a list with all available terms the user can search for:
* `Fini >> -t list`

**TERM**
This option will display all the information available about the particular TERM. The user can input multiple terms in a row, separated by space and the application will output the descriptions one after the other. If a command is not recognised, the appliction will inform the user. For example the following will display the definition of EPS:
* `Fini >> -t eps`

[NOTE]: the terms are case insensitive; so the following commands fo the same thing:
* `Fini >> -t PE`
* `Fini >> -t pe`

OR:
* `Fini >> -t eps pe`
* `Fini >> -t EPS PE`
* `Fini >> -t eps PE`
etc.

# -c, --cls
This command clears the screen.

# -q, --quit
This commands exits the application.

## Features

## Installation 
