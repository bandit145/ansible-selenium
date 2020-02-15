#!/usr/bin/env python
# Copyright (c) 2018 Philip Bove <pgbson@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = 'TODO'
EXAMPLES = '''
	- name: configure zabbix
	  selenium:
	   uri: http://webpage.com/
	   actions:
	    - "element":"thing"
	       action: "send_keys"
	       data: "texttotype"
	       get_element_by: "name"
	    - "element": "thing"
	       action: "click"
	       get_element_by: "xpath"
'''	

from ansible.module_utils.basic import *

try:
	from selenium import webdriver
	from selenium.common.exceptions import *
	from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
	HAS_SELENIUM = True
except:
	HAS_SELENIUM = False

def check_data(module):
	for action in module.params['actions']:
		fail = (False,None)
		#module.fail_json(msg=action)
		if 'element' not in action.keys():
			fail = (True,'element')
		elif 'action' not in action.keys():
			fail = (True,'action')
		elif 'get_element_by' not in action.keys():
			fail = (True,'get_element_by')
		elif action['action'] != 'click' and 'data' not in action.keys():
			fail = (True,'data')
		if fail[0]:
			module.fail_json(msg='selenium action {number} is missing {missing}'.format(number=module.params['actions'].index(action)+1,missing=fail[1]))

def configure_driver(module):
	try:
		options = webdriver.ChromeOptions()
		options.set_headless()
		#so no cookies or anything is saved
		options.add_argument('--incognito')
		options.add_argument('--disable-gpu')
		#enter weird solution found here https://bugs.chromium.org/p/chromium/issues/detail?id=721739#c106
		#thanks mbacko
		capabilities = DesiredCapabilities.CHROME.copy()
		if not module.params['validate_certs']:
			options.add_argument('--ignore-certificate-errors')
	except Exception as error:
		module.fail_json(msg=str(error))
		
	driver = webdriver.Chrome(chrome_options=options, desired_capabilities=capabilities)
	driver.set_window_size(module.params['window_width'],module.params['window_length'])
	if module.params['wait']:
		driver.implicitly_wait(module.params['wait'])
	return driver

def run_selenium(module):
	driver = configure_driver(module)
	try:
		driver.get(module.params['url'])
		for action in module.params['actions']:
			element = getattr(driver,'find_element_by_'+action['get_element_by'])(action['element'])
			if action['action'] == 'click':
				getattr(element,action['action'])()
			else:
				getattr(element,action['action'])(action['data'])
		#this is kinda weird but if it's expecting an element and it's not there it will fail, it shouldn't continue and say unchanged
		#therefore if this all works it will always be true
		driver.close()
		module.exit_json(changed=True)
	except NoSuchElementException as error:
		driver.close()
		module.fail_json(msg="Could not find element. Full Error: {element}".format(element=str(error)))
	except Exception as error:
		driver.close()
		module.fail_json(msg=str(error))

def main():
	module = AnsibleModule(
			argument_spec = dict(
				url = dict(type=str,required=True),
				wait = dict(type=int,default=1),
				actions = dict(type=list, requried=True),
				window_width = dict(type=int,default=1920),
				window_length = dict(type=int,default=1080),
				validate_certs = dict(type=bool,default=True)
			),
			supports_check_mode=False
		)
	if not HAS_SELENIUM:
		module.fail_json(msg='selenium is not installed')
	check_data(module)
	run_selenium(module)

if __name__ == '__main__':
	main()