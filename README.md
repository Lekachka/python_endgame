# Endgame Rest API Client
```
_____________________________________________________
```

## Description:

The Endgame Rest API Client project provides REST API requests.  
Program send GET, POST, PUT, PATCH, DELETE request according to the input parameters, gets the response and shows it in several formats or error message if any.   
Provides CLI and GUI interfaces. The CLI interface is default one.

## Prerequisites

Python3.x should be installed in the system.

Use istractions from offisial site for installation: https://www.python.org/downloads/

Another needed packages should be istalled:  
pip install prettytable  
pip install pyyaml  
pip install tkinter  

## Usage
Program is runnig under console with user defined arguments.  
To run GUI interface use -g (--gui) param, otherwise define request parameters and optionally log level and/or response view.  
Also, you can see or clear request history in both CLI and GUI mode using --history show/clear arguments in CLI mode or pressing .  
You can use hidden parameters in both mode using {@dictionary_key} instead of dictionary value if parameter was used in previous request. 
Run program help with -h (--help) argument for show program help.
Using GUI 

```
optional arguments:
===================
```
-   -h, --help            show this help message and exit
-   -g, --gui             set GUI mode
-   --history {show,clear}
                        show/clear history
-   -m {GET,POST,PUT,PATH,DELETE}, --method {GET,POST,PUT,PATH,DELETE}
                        set HTTP verb
-   -e ENDPOINT, --endpoint ENDPOINT
                        set URL
-   -p PARAMS [PARAMS ...], --params PARAMS [PARAMS ...]
                        set URL parameters
-   --headers HEADERS [HEADERS ...]
                        set URL headers
-   -b BODY [BODY ...], --body BODY [BODY ...]
                        set request body in format: "key"="value"
-   -a USER PASSWORD, --auth USER PASSWORD
                        set Username and Password
-   -l {WORNING,INFO,ERROR,DEBUG}, --log {WORNING,INFO,DEBUG}
                        Set logging level
-   -v {json,yaml,txt,tree}, --view {json,yaml,txt,tree}
                        Set recponce view

```
Examples:
=========
```
```
1.  python endgame.py --help
2.  python endgame.py --method GET --endpoint https://api.github.com/events -l "DEBUG" -v 'yaml'
3.  python endgame.py -g
```
![Alt-текст](https://i.ibb.co/Q8GzRgx/GUI.png "GUI")
```
4.  python endgame.py --method POST --endpoint https://reqres.in/api/users --body name="paul rudd" movies="I Love You" --auth user 123
5.  python endgame.py -m GET --endpoint http://jsonplaceholder.typicode.com/posts/79 --headers "user-agent"={@user-agent} "Accept"={@Accept} --auth {@user} {@pass}
```
## Authors

Vlad Hlushchenko (vhlushchen@student.ucode.world): GUI, Presentation  
Olena Oliinyk (ooliinyk@student.ucode.world): ClI, Requests, Logging  
Andrii Bozhok (abozhok@student.ucode.world): Data Base, History, Table Views