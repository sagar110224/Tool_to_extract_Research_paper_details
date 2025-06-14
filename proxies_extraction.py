from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import zipfile
import requests, queue
import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class extract_valid_proxies:
    def __init__(self):
        pass
    def load_proxy_components(self):
        with open('/Users/drago/Documents/Practicefiles/Data_files/proxy_list.txt','r') as f:
            proxies=f.read()
        proxy_host=[]
        proxy_port=[]
        proxy_user=[]
        proxy_pass=[]
        proxy_list=proxies.split('\n')
        proxy_list=proxy_list[:-2]
        for proxy in proxy_list:
            p=proxy.split(":")
            proxy_host.append(p[0])
            proxy_port.append(p[1])
            proxy_user.append(p[2])
            proxy_pass.append(p[3])
        return proxy_list,proxy_host,proxy_port,proxy_user,proxy_pass
    
    def create_proxy_extension(self,ip,port,user,password):
        manifest_json = """
        {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }
        """

        background_js = f"""
        var config = {{
                mode: "fixed_servers",
                rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{ip}",
                    port: parseInt({port})
                }},
                bypassList: ["localhost"]
                }}
            }};
        chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

        chrome.webRequest.onAuthRequired.addListener(
            function(details) {{
                return {{
                    authCredentials: {{
                        username: "{user}",
                        password: "{password}"
                    }}
                }};
            }},
            {{urls: ["<all_urls>"]}},
            ['blocking']
        );
        """
        plugin_file_path = f'proxy_auth_plugin_{ip}.zip'
        with zipfile.ZipFile(plugin_file_path, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        return plugin_file_path
    
    def check_proxies(self):
        valid_proxies=[]
        proxy_list,ip,port,user,password=self.load_proxy_components()
        for idx in range(len(ip)):
            plugin_path=self.create_proxy_extension(ip[idx],port[idx],user[idx],password[idx])
            chrome_options = Options()
            chrome_options.add_extension(plugin_path)
            driver = webdriver.Chrome(options=chrome_options)
            try:
                driver.get("https://developer.mozilla.org/en-US/docs/Learn_web_development/Howto/Tools_and_setup/set_up_a_local_testing_server")
                WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
                page = driver.page_source
                if page.strip():
                    valid_proxies.append(proxy_list[idx])
                else:
                    # print(f'{proxy_list[idx]} not valid')
                    continue
                # print("IP returned by proxy:", driver.page_source)

                
            finally:
                driver.quit()
                os.remove(plugin_path)
        
        return valid_proxies
