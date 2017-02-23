import af_support_tools
import json
import requests
from requests.packages.urllib3.exceptions import InsecurePlatformWarning, InsecureRequestWarning, ConnectionError
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
#import pdb; pdb.set_trace()

try:
    env_file = 'env.ini'
except:
    print('Possible Configuration Error')

def get_auth(hostname, username, password):
    """
    Function designed to return to the caller the auth token required to access the vAPI.
    Example: cookies = get_auth(hostname, username, password)
    """
    # Build up base URLS
    base_url = 'https://' + hostname + ':443'
    tickets_url = base_url + '/cas/v1/tickets'
    cvm_auth_url = base_url + '/cvm/auth'
    # Ticket Granting Ticket
    try:
        tgt = requests.request('POST', url=tickets_url, data={'username': username, 'password': password}, verify=False)
    except requests.exceptions.ConnectionError as e:
        raise Exception ('Could not connect to ' + hostname)
    if tgt.status_code != 201:
        raise Exception('Unable to connect to CAS server')
    st_url = tgt.headers['Location']
    # Service Ticket
    st = requests.request('POST', url=st_url, data='service=' + cvm_auth_url, verify=False)
    # Get Cookie Jar to chain to data requests
    cj = requests.request('POST', url=cvm_auth_url + '?ticket=' + st.text, verify=False, allow_redirects=False)
    if len(cj.cookies) == 0:
        raise Exception('No cookie returned from CAS server')
    return(cj.cookies)

def build_url_request_json(hostname='hostname_not_passed', username='username_not_passed', password='password_not_passed', query_string='query_string__not_passed'):
    """
    Function designed to return to the caller a build URL string to pass to the vAPI for a json response.
    Example: json_string = build_url_request_json(hostname=hostname, username=username, password=password, query_string=query_string)
    """
    if hostname == 'hostname_not_passed':
        hostname = af_support_tools.get_config_file_property(config_file=env_file, heading='vapi_settings', property='vapi_hostname')
    if username == 'username_not_passed':
        username = af_support_tools.get_config_file_property(config_file=env_file, heading='vapi_settings', property='vapi_username')
    if password == 'password_not_passed':
        password = af_support_tools.get_config_file_property(config_file=env_file, heading='vapi_settings', property='vapi_password')
    vblocks_url = 'https://' + hostname + '/cvm/mvmgmt/queries?from=0&q=find ' + query_string + '&size=500'
    data = requests.request('GET', url=vblocks_url, verify=False, cookies=get_auth(hostname, username, password))
    return(data.json())

def get_json_by_query(hostname='hostname_not_passed', username='username_not_passed', password='password_not_passed',query_string='query_string_not_passed'):
    """
    Function designed to return to the caller a json string from the vAPI based off of the query string passed.
    Example: data_json = get_json_by_query(query_string=’Datacenter’)
    """
    json_string = build_url_request_json(hostname=hostname, username=username, password=password, query_string=query_string)
    return(json_string)

