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