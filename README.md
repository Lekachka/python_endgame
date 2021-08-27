# Description of Endgame Rest API Client project

The Endgame Rest API Client project provides REST API requests, gets and shows the response or error message, provides CLI and GUI interfaces. The CLI interface is default one.
```
____
```

```
optional arguments:
===========
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
-   -l {WORNING,INFO,ERROR,DEBUG}, --log {WORNING,INFO,ERROR,DEBUG}
                        Set logging level
-   -v {json,yaml,txt,tree}, --view {json,yaml,txt,tree}
                        Set recponce view

```
Examples:
===========
```
```
1.  python endgame.py --help
2.  python endgame.py --method GET --endpoint https://api.github.com/events
3.  python endgame.py -g
4.  python endgame.py --method POST --endpoint https://reqres.in/api/users --body name="paul rudd" movies="I Love You" --auth user 123
5.  python endgame.py -m GET --endpoint http://jsonplaceholder.typicode.com/posts/79 --headers "user-agent"={@user-agent} "Accept"={@Accept} --auth {@user} {@pass}
