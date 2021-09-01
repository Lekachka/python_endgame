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


def log_basic_config():
    logging.basicConfig(filename='endgame.log',
                        filemode='a',
                        format='[%(levelname)7s]: %(message)s'
                        )
    return logging.getLogger('endgame')


m_logger = log_basic_config()


parser = argparse.ArgumentParser(prog='Rest API Client',
                                 usage='%(prog)s [options]',
                                 description="Endgame Rest API Client",
                                 # epilog="Examples:\n" + "\n".join(epilog_examples),
                                 formatter_class=argparse.RawTextHelpFormatter)


def parce_cli_args():
    """"Parce the input args, don't check the required hire"""
    epilog_examples = ['python endgame.py --help',
                       'python endgame.py --method GET --endpoint https://api.github.com/events',
                       'python endgame.py -g',
                       'python endgame.py --method POST --endpoint https://reqres.in/api/users '
                       '--body name="paul rudd" movies="I Love You" --auth user 123',
                       'python endgame.py -m GET --endpoint http://jsonplaceholder.typicode.com/posts/79 '
                       '--headers "user-agent"={@user-agent} "Accept"={@Accept} --auth {@user} {@pass}']
    parser.epilog = "Examples:\n" + "\n".join(epilog_examples)

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
                        choices=['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                        action='store',
                        help='set HTTP verb',
                        default='GET'
                        )
    parser.add_argument('-e', '--endpoint',
                        dest='url',
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
                        choices=['WORNING', 'INFO', 'DEBUG'],
                        help='Set logging level'
                        )
    parser.add_argument('-v', '--view',
                        help='Set recponce view',
                        choices=['json', 'yaml', 'txt', 'tree'],
                        default='json',
                        dest='view'
                        )
    return parser.parse_args()


pars_args = parce_cli_args()
request_dict = {}  # API Request params dictionary
var_file_name = 'vars.yaml'
full_resp: requests = None


def print_view(resp, view='json', gui=False):
    try:
        view_dict = {
            'json': json.dumps(resp if isinstance(resp, dict) else resp.json(), indent=2),
            'yaml': yaml.dump(resp if isinstance(resp, dict) else resp.text, sort_keys=False, default_flow_style=False),
            'raw': resp if isinstance(resp, dict) else resp.content
        }
        return view_dict[view]
    except Exception as e:
        return "Failed"


def vars_from_files(file_name: str):
    """Loads variables for yaml file"""
    try:
        with open(file_name, 'r') as yaml_file:
            return yaml.safe_load(yaml_file)
    except:
        m_logger.debug("Error while processing YAML file")
        return {}


def change_hidden_var(diction: dict):
    """Check the hided variables in yaml file"""
    local_request_dict = json.loads(json.dumps(diction))
    yaml_loaded_dict = vars_from_files(var_file_name)  # load variables from yaml file
    for k, i in local_request_dict.items():
        if i and isinstance(i, str) and re.search(r"{@.+}", i):  # Если значение словаря сущ-т, явл. Cтрокой
            new_item = str(yaml_loaded_dict.get(k, None))  # и содержится в {@} - меняем в словаре скрытое
            local_request_dict.update({k: new_item})  # значение на значение из файла
        elif i and isinstance(i, dict):  # Если .. и явл. Словарём - перебираем значения
            for y, z in i.items():  # вложенного словаря.
                if z and isinstance(z, str) and re.search(r"{@.+}", z):
                    new_item = str(yaml_loaded_dict.get(k, None).get(y, None))
                    if new_item:
                        i.update({y: new_item})
        elif i and isinstance(i, list):  # Если значение словаря сущ-т, явл. Списком
            for y, z in enumerate(i):  # и содержится в {@} - меняем в списке скрытое
                if re.search(r"{@.+}", z):  # значение на значение из файла
                    if yaml_loaded_dict.get(k, None):
                        i[y] = str(yaml_loaded_dict.get(k, None)[y])
                        local_request_dict.update({k: i})

    return local_request_dict


class Req (object):
    """Create class for requests"""
    def __init__(self, req_params: dict, view='json'):
        tmp_dict = {}
        tmp_dict = change_hidden_var(req_params)
        self.url = tmp_dict.get('url', None)
        self.method = tmp_dict.get('method', None)
        self.params = tmp_dict.get('params', None)
        self.body = tmp_dict.get('body', None)
        self.headers = tmp_dict.get('headers', None)
        self.auth = tmp_dict.get('auth', None)
        self.method_dict = {'GET': self.get_request,
                            'POST': self.post_request,
                            'PUT': self.put_request,
                            'PATCH': self.patch_request,
                            'DELETE': self.del_request
                            }
        self.view = view
        m_logger.debug(f'Request obj created with/without hidden params: {str(req_params)}')
        m_logger.debug(f'Request obj created with decoded params {str(tmp_dict)}')

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
            m = 'Rest API Client: error: the following arguments are required: -e/--endpoint'
            #m_logger.error('m')
            return False, m
        elif not re.match(regex, self.url):
            m = f'URL {self.url} is invalid'
            return False, m
        else:
            return True, ''

    def get_request(self):                              # Create get method
        url_ck, m = self.check_url()
        if url_ck:
            resp = requests.get(self.url,
                                params=(self.params or self.body),
                                auth=None if not self.auth else (self.auth[0], self.auth[1]),
                                headers=None if not self.headers else self.headers
                                )
            return resp, ''
        else:
            return False, m

    def put_request(self):                              # Create put method
        url_ck, m = self.check_url()
        if url_ck:
            resp = requests.put(self.url,
                                data=(self.params or self.body),
                                auth=None if not self.auth else (self.auth[0], self.auth[1]),
                                headers=self.headers
                                )
            return resp, ''
        else:
            return False, m

    def del_request(self):                              # Create del method
        url_ck, m = self.check_url()
        if url_ck:
            resp = requests.delete(self.url,
                                   params=(self.params or self.body),
                                   auth=None if not self.auth else (self.auth[0], self.auth[1]),
                                   headers=self.headers
                                   )
            return resp, ''
        else:
            return False, m

    def patch_request(self):                            # Create patch method
        url_ck, m = self.check_url()
        if url_ck:
            resp = requests.patch(self.url,
                                  params=(self.params or self.body),
                                  auth=None if not self.auth else (self.auth[0], self.auth[1]),
                                  headers=self.headers
                                  )
            return resp, ''
        else:
            return False, m

    def post_request(self):                             # Create post method
        url_ck, m = self.check_url()
        if url_ck:
            resp = requests.post(self.url,
                                 data=(self.params or self.body),
                                 auth=None if not self.auth else (self.auth[0], self.auth[1]),
                                 headers=self.headers
                                 )
            return resp, ''
        else:
            return False, m


req_inst = Req(request_dict, None)  # create Request class instance

MainTable = PrettyTable()
MainTable.field_names = ['N', 'Method', 'URL', 'Params', 'Request body', 'Status']
#  decorator for output
SecondaryTable = PrettyTable(['..', 'Request info'])

connect = sqlite3.connect('history.db')
#  create connect to history.db. It allready have main Table History
cursor = connect.cursor()
#  create cursor
main_table = 'CREATE TABLE IF NOT EXISTS history (N integer primary key, Method text, URL text, Params text, ' \
             'Headers text, Request_body text, Authentification text, status int , response text);'
cursor.execute(main_table)


def print_stderr(er_mess):
    print(f"ERROR| {er_mess}.", file=sys.stderr)


def print_stdout(inf_mess):
    print(f"INFO | {inf_mess}.", file=sys.stdout)


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


def gui_start():
    root = tk.Tk()
    venv.MainApplication(root).pack(side="top", fill="both", expand=True)
    root.title("END GAME")
    root.resizable(False, False)
    root.mainloop()
    sys.exit(2)


def create_request_dict():
    """ Create dictionary with request paramiters"""
    local_request_dict = {}
    local_request_dict['body'] = {}
    local_request_dict['params'] = {}
    local_request_dict['headers'] = {}

    if pars_args.url:  # add endpoint param to dict. will be checked latter
        local_request_dict['url'] = pars_args.url
    else:
        local_request_dict['url'] = None

    if pars_args.method:
        local_request_dict['method'] = pars_args.method
    else:
        local_request_dict['method'] = 'GET'

    if pars_args.params:
        for item in pars_args.params:
            if re.match(r"^.+=.+$", item):
                local_request_dict['params'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        local_request_dict['params'] = None

    if pars_args.body:
        for item in pars_args.body:
            if re.match(r"^.+=.+$", item):
                local_request_dict['body'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        local_request_dict['body'] = None

    if pars_args.headers:
        for item in pars_args.headers:
            if re.match(r"^.+=.+$", item):
                local_request_dict['headers'].update({item.split('=')[0]: item.split('=')[1]})
    else:
        local_request_dict['headers'] = None

    if pars_args.auth:
        local_request_dict['auth'] = pars_args.auth
        m_logger.debug('Request auth: ' + str(local_request_dict['auth']))
    else:
        local_request_dict['auth'] = None

    return local_request_dict


def run_query(inp_dict: dict, inp_req_inst):
    my_resp: requests
    tem_dict = {}
    my_resp, l_mess = inp_req_inst.method_dict[inp_req_inst.method]()           # Run needed method with Req instance
    my_resp.raise_for_status()
    if my_resp is not None and not my_resp.ok:
        m_logger.error(f'Request to {inp_req_inst.url} is faild. '
                       f'Error code {my_resp.status_code} {my_resp.reason}')
        l_mess = (f'Request to {inp_req_inst.url} is failed. '
                  f'Error code {my_resp.status_code} {my_resp.reason}')
    elif my_resp:
        try:
            for i in ['auth', 'body', 'headers', 'method', 'params', 'url']:
                if hasattr(inp_req_inst, i):
                    tem_dict[i] = inp_req_inst.__getattribute__(i)
            with open(var_file_name, 'w') as var_file:  # Write request dictionary to yaml file
                yaml.dump(tem_dict, var_file)
        except (OSError, IOError):
            pass
        count_rows = cursor.execute("select count(*) from history;").fetchone()
        m_logger.debug(f'count_rows {str(count_rows)}')
        if len(count_rows) > 0:
            N = count_rows[0]
        else:
            N = 0
        met = str(inp_dict['method'])
        url = str(inp_dict['url'])
        auth = str(json.dumps(inp_dict.get('auth', None)))
        code = my_resp.status_code
        prms = str(json.dumps(inp_dict.get('params', None), indent=0))
        hdrs = str(json.dumps(inp_dict.get('headers', None), indent=0))
        bdy = str(json.dumps(inp_dict.get('body', None), indent=0))
        rez = str(json.dumps(json.loads(my_resp.text), indent=0))[1:-1]
        data = (N, met, url, prms, hdrs, bdy, auth, code, rez)
        cursor.execute(f"insert into history values(?, ?, ?, ?, ?, ?, ?, ?, ?);", data)
        connect.commit()
        m_logger.info(f'Got response {my_resp.status_code} {my_resp.reason} '
                      f'from {req_inst.url} in {my_resp.elapsed.total_seconds()} seconds')
        l_mess = ''
    return my_resp, l_mess


def cli():
    if pars_args.log:  # set log level to user defined if arg exists, else set INFO
        m_logger.setLevel(pars_args.log)
    else:
        m_logger.setLevel(logging.INFO)

    if pars_args.history:  # run History show or cleaning if arg exists
        history = pars_args.history
        method_history = {
            'show': history_show,
            'clear': history_clear
        }
        method_history[history]()
    request_dict = create_request_dict()  # Create dictionary for request paramiters
    local_inst = Req(request_dict, pars_args.view)  # create Request class instance
    m_logger.info(f'Send {local_inst.method} request to {local_inst.url}')
    local_resp: requests = None
    try:
        local_resp, mess = run_query(request_dict, local_inst)
        if local_resp:
            print(f'---Got response {local_resp.status_code} {local_resp.reason} '
                  f'in {str(round(local_resp.elapsed.total_seconds(), 2))} seconds---')
            print('---Response body---')
            print(print_view(local_resp, pars_args.view, pars_args.gui))
        else:
            print_stderr(mess)
            pass
    except requests.exceptions.RequestException as e:
        m_logger.error(f'<{local_inst.method}> request Faild with error:           {e}')
        print_stderr(f'<{local_inst.method}> request Faild.\n       {e}')
    except json.decoder.JSONDecodeError as e:               # Can not decode responce to json format
        if pars_args.view and pars_args.view == 'json':     # if JSON is used as 'view' argument show errors
            m_logger.error('json deconding error')
            print_stderr('json deconding error')
        if local_resp is not None and local_inst:
            print(local_resp.text)
    except Exception as e:
        print_stderr(f'<{local_inst.method}> request Faild.\n       {e}')


if __name__ == '__main__':
    if pars_args.gui:                                       # start GUI mode
        gui_start()
    else:
        cli()                                               # start CLI mode
