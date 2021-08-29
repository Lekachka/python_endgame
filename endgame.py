import requests
import re
import sys
import argparse
import logging
import json
import yaml
import sqlite3
from prettytable import PrettyTable
import tkinter as tk
import venv


MainTable = PrettyTable()
MainTable.field_names = ['N', 'Method', 'URL', 'Params', 'Request body', 'Status']
#  decorator for output
SecondaryTable = PrettyTable(['..', 'Request info'])

connect = sqlite3.connect('history.db')
#  create connect to history.db. It allready have main Table History
cursor = connect.cursor()
#  create cursor
main_table = 'CREATE TABLE IF NOT EXISTS history (N integer primary key, Method text, URL text, Params text, Headers text, Request_body text, Authentification text, status int , response text);'
cursor.execute(main_table)


def print_stderr(mess):
    print(f"ERROR| {mess}.", file=sys.stderr)


def print_stdout(mess):
    print(f"INFO | {mess}.", file=sys.stdout)


class Req (object):  # Create class for requests
    def __init__(self, req_params: dict):
        self.url = req_params.get('endpoint', None)
        self.method = req_params.get('method', None)
        self.params = req_params.get('params', None)
        self.body = req_params.get('body', None)
        self.headers = req_params.get('headers', None)
        self.auth = req_params.get('auth', None)
        m_logger.debug(f'Request obj created with params {str(req_params)}')

    def __str__(self):
        return f'<Class {self.__class__.__name__} object>:\nURl: {self.url}\nmethod: {self.method}\nauth: {self.auth}'

    def check_url(self):  # check the entered URL
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|)'  # ...or ip            
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        if not self.url:
            m_logger.error('Rest API Client: error: the following arguments are required: -e/--endpoint')
            print_stderr('Rest API Client: error: the following arguments are required: -e/--endpoint')
        elif not re.match(regex, self.url):
            m_logger.error(f'URL {self.url} is invalid')
            print_stderr('The site URL format is invalid')
            sys.exit(1)
        else:
            return True

    def get_request(self):                              # Create get method
        self.check_url()
        resp = requests.get(self.url,
                            params=(self.params or self.body),
                            auth=None if not self.auth else (self.auth[0], self.auth[1]),
                            headers=self.headers
                            )
        return resp

    def put_request(self):                              # Create put method
        self.check_url()
        resp = requests.put(self.url,
                            data=(self.params or self.body),
                            auth=None if not self.auth else (self.auth[0], self.auth[1]),
                            headers=self.headers
                            )
        return resp

    def del_request(self):                              # Create del method
        self.check_url()
        resp = requests.delete(self.url,
                               params=(self.params or self.body),
                               auth=None if not self.auth else (self.auth[0], self.auth[1]),
                               headers=self.headers
                               )
        return resp

    def patch_request(self):                            # Create patch method
        self.check_url()
        resp = requests.patch(self.url,
                              params=(self.params or self.body),
                              auth=None if not self.auth else (self.auth[0], self.auth[1]),
                              headers=self.headers
                              )
        return resp

    def post_request(self):                             # Create post method
        self.check_url()
        resp = requests.post(self.url,
                             data=(self.params or self.body),
                             auth=None if not self.auth else (self.auth[0], self.auth[1]),
                             headers=self.headers
                             )
        return resp


def history_show():
    count_rows = cursor.execute("select count(*) from history;").fetchone()[0]
    cursor.execute("select * from history;")
    tabl = cursor.fetchmany(count_rows)
    for row in tabl:
        MainTable.add_row([row[0], row[1], row[2], row[3], row[5], row[7]])
    print(MainTable)
    choose = input('Enter request index to view full info, or "q" to quit: ')
    if choose == 'q':
        cursor.close()
        connect.close()
        exit()
    elif int(choose) <= count_rows:
        data_list = cursor.execute(f'SELECT * FROM history where N={choose};').fetchone()
        history_list = ['N', 'Method', 'URL', 'Params', 'Headers', 'Request body', 'Basic Authentication', 'Status',
                        'Response']
        for i in range(len(data_list)-1):
            SecondaryTable.add_row([history_list[i], data_list[i]])
        print(SecondaryTable)
        print(f'---Response---\n{data_list[-1]}')
        cursor.close()
        connect.close()
        exit()
    else:
        print('Wrong input')
        exit()


def history_clear():
    cursor.execute('drop table history;')
    connect.commit()
    cursor.close()
    connect.close()
    print('---Request history cleared---')
    exit()


def print_view(resp, view, gui):
    view_dict = {       # 'json': json.dumps(json.loads(resp.text), indent=2),
                 'json': json.dumps(resp.json(), indent=2),
                 'yaml': yaml.dump(resp.text, sort_keys=False, default_flow_style=False),
                 'txt':  resp.text,
                 'raw':  resp.content,
                 'tree': 'Can not build tree view in CLI mode' if not gui else ''       # to do
                 }
    return view_dict[view]


def gui_start(diction, view):
    root = tk.Tk()
    venv.MainApplication(root).pack(side="top", fill="both", expand=True)
    root.title("END GAME")
    root.mainloop()
    sys.exit(2)


def parce_cli_args():
    pass


def vars_from_files(file_name: str):
    with open(file_name, 'r') as yaml_file:
        try:
            return yaml.safe_load(yaml_file)
        except (OSError, IOError):
            return {}


if __name__ == '__main__':
    """
        Logging configuration
    """
    logging.basicConfig(filename='endgame.log',
                        filemode='a',
                        format='[%(levelname)7s]: %(message)s'
                        )
    m_logger = logging.getLogger('endgame')
    epilog_examples = ['python endgame.py --help',
                       'python endgame.py --method GET --endpoint https://api.github.com/events',
                       'python endgame.py -g',
                       'python endgame.py --method POST --endpoint https://reqres.in/api/users '
                       '--body name="paul rudd" movies="I Love You" --auth user 123',
                       'python endgame.py -m GET --endpoint http://jsonplaceholder.typicode.com/posts/79 '
                       '--headers "user-agent"={@user-agent} "Accept"={@Accept} --auth {@user} {@pass}']
    """
        Argument parcer configuration
    """
    parser = argparse.ArgumentParser(prog='Rest API Client',
                                     usage='%(prog)s [options]',
                                     description="Endgame Rest API Client",
                                     epilog="Examples:\n" + "\n".join(epilog_examples),
                                     formatter_class=argparse.RawTextHelpFormatter)
    if len(sys.argv) == 1:
        parser.print_usage()
        exit()

    parser.add_argument('-g', '--gui',
                        action='store_true',
                        dest='gui',
                        help='set GUI mode',
                        )
    parser.add_argument('--history',
                        choices=['show', 'clear'],
                        action='store',
                        help='show/clear history'
                        )
    parser.add_argument('-m', '--method',
                        dest='method',
                        choices=['GET', 'POST', 'PUT', 'PATH', 'DELETE'],
                        action='store',
                        help='set HTTP verb',
                        default='GET'
                        )
    parser.add_argument('-e', '--endpoint',
                        dest='endpoint',
                        action='store',
                        # required=True,
                        help='set URL'
                        )
    parser.add_argument('-p', '--params',
                        nargs='+',
                        help='set URL parameters'
                        )
    parser.add_argument('--headers',
                        dest='headers',
                        nargs='+',
                        help='set URL headers'
                        )
    parser.add_argument('-b', '--body',
                        nargs='+',
                        dest='body',
                        help='set request body in format: "key"="value"'
                        )
    parser.add_argument('-a', '--auth',
                        action='store',
                        nargs=2,
                        dest='auth',
                        metavar=("USER", "PASSWORD"),
                        help='set Username and Password'
                        )
    parser.add_argument('-l', '--log',
                        choices=['WORNING', 'INFO', 'ERROR', 'DEBUG'],
                        help='Set logging level'
                        )
    parser.add_argument('-v', '--view',
                        help='Set recponce view',
                        choices=['json', 'yaml', 'txt', 'tree'],
                        default='json'
                        )

    pars_args = parser.parse_args()

    if pars_args.log:                                   # set log level to user defined if arg exists, else INFO level
        m_logger.setLevel(pars_args.log)
    else:
        m_logger.setLevel(logging.INFO)

    if pars_args.history:                               # run History show or cleaning if arg exists
        history = pars_args.history
        method_history = {
            'show': history_show,
            'clear': history_clear
        }
        method_history[history]()
    """
    Create dictionary for request paramiters
    """
    request_dict = {}
    request_dict['body'] = {}
    request_dict['params'] = {}
    request_dict['headers'] = {}

    if pars_args.endpoint:                              # add endpoint param to dict. will be checked latter
        request_dict['endpoint'] = pars_args.endpoint
    else:
        request_dict['endpoint'] = None

    if pars_args.method:
        request_dict['method'] = pars_args.method
    else:
        request_dict['method'] = 'GET'

    if pars_args.params:
        for item in pars_args.params:
            if re.match(r"^.+=.+$", item):
                request_dict['params'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        request_dict['params'] = None

    if pars_args.body:
        for item in pars_args.body:
            if re.match(r"^.+=.+$", item):
                request_dict['body'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        request_dict['body'] = None

    if pars_args.headers:
        for item in pars_args.headers:
            if re.match(r"^.+=.+$", item):
                request_dict['headers'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        request_dict['headers'] = None

    if pars_args.auth:
        request_dict['auth'] = pars_args.auth
    else:
        request_dict['auth'] = None

    var_file_name = 'vars.yaml'
    yaml_loaded_dict = vars_from_files(var_file_name)       # load variables from yaml file
    """
    Check the hided variables in yaml file
    """
    for k, i in request_dict.items():
        if i and isinstance(i, str) and re.search(r"{@.+}", i):     # Если значение словаря сущ-т, явл. Cтрокой
            new_item = str(yaml_loaded_dict.get(k, None))           # и содержится в {@} - меняем в словаре скрытое
            request_dict.update({k: new_item})                      # значение на значение из файла
        elif i and isinstance(i, dict):                             # Если .. и явл. Словарём - перебираем значения
            for y, z in i.items():                                  # вложенного словаря.
                if z and isinstance(z, str) and re.search(r"{@.+}", z):
                    new_item = str(yaml_loaded_dict.get(k, None)[y])
                    if new_item:
                        i.update({y: new_item})
        elif i and isinstance(i, list):                             # Если значение словаря сущ-т, явл. Списком
            for y, z in enumerate(i):                               # и содержится в {@} - меняем в списке скрытое
                if re.search(r"{@.+}", z):                          # значение на значение из файла
                    i[y] = str(yaml_loaded_dict.get(k, None)[y])
                    request_dict.update({k: i})

    req_inst = Req(request_dict)                            # create Request class instance
    method_dict = {
        'GET': req_inst.get_request,
        'POST': req_inst.post_request,
        'PUT': req_inst.put_request,
        'PATCH': req_inst.patch_request,
        'DELETE': req_inst.del_request
    }

    if pars_args.gui:                                       # start GUI mode
        gui_start(method_dict, pars_args.view)

    m_logger.info(f'Send {req_inst.method} request to {req_inst.url}')

    responce: requests = None
    try:
        responce = method_dict[req_inst.method]()           # Run needed method with Req instance
        print(f'---Got response {responce.status_code} {responce.reason} '
              f'in {str(round(responce.elapsed.total_seconds(),2))} seconds---')
        with open(var_file_name, 'w') as var_file:          # Write request dictionary to yaml file
            yaml.dump(request_dict, var_file)
        if not responce.ok:
            m_logger.error(f'Request to {req_inst.url} is faild. '
                           f'Error code {responce.status_code} {responce.reason}')
        else:
            count_rows = cursor.execute("select count(*) from history;").fetchone()
            m_logger.debug(f'count_rows {str(count_rows)}')
            if len(count_rows) > 0:
                N = count_rows[0]
            else:
                N = 0
            met = str(request_dict['method'])
            url = str(request_dict['endpoint'])
            auth = str(json.dumps(request_dict['auth']))
            code = responce.status_code
            prms = str(json.dumps(request_dict['params'], indent=0))
            hdrs = str(json.dumps(request_dict['headers'], indent=0))
            bdy = str(json.dumps(request_dict['body'], indent=0))
            rez = str(json.dumps(json.loads(responce.text), indent=0))[1:-1]
            data = (N, met, url, prms, hdrs, bdy, auth, code, rez)
            cursor.execute(f"insert into history values(?, ?, ?, ?, ?, ?, ?, ?, ?);", data)
            connect.commit()

            m_logger.info(f'Got response {responce.status_code} {responce.reason } '
                          f'from {req_inst.url} in {responce.elapsed.total_seconds()} seconds')
            print('---Response body---')
            print(print_view(responce, pars_args.view, pars_args.gui))
    except requests.exceptions.RequestException as e:
        m_logger.error(f'<{req_inst.method}> request Faild.\n           {e}')
        print_stderr(f'<{req_inst.method}> request Faild.\n       {e}')
    except json.decoder.JSONDecodeError as e:               # Can not decode responce to json format
        if pars_args.view and pars_args.view == 'json':     # if JSON is used as 'view' argument show errors
            m_logger.error('json deconding error')
            print_stderr('json deconding error')
        if responce:
            print(responce.text)
