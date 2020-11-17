import time
import os
import signal
import subprocess
from threading import Thread
import sys
import glob
from exceptions import IOError
from ping import ping
import pprint

CONFIG_FILE = os.path.join(os.environ['HOME'], '.config', 'online-status-indicator', 'settings.conf')
ICON_FORMAT = 'svg'

class IndicatorUpdateThread(Thread):
    _default_config = {
        'icon_theme': 'default',
        'hosts': ['8.8.8.8'],
        'launchers': [{'text': 'Settings', 'command': 'xdg-open ' + CONFIG_FILE}]
    }
    
    
    def __init__(self, indicator):
        super(IndicatorUpdateThread, self).__init__()
        self._indicator = indicator
        self._exit = False
        self._next_host = 0
        self._menu_description = []
        self._launchers = []
        self.load_config(CONFIG_FILE)
        self._menu_description = self.build_menu_description()
        self._indicator.update_menu(self._menu_description)
    

    def build_menu_description(self):
        menu_description = []
        for item in self._launchers:
            menu_description.append(item)
        menu_description.append({'text': 'Quit', 'activate': self._on_menu_item_quit})
        return menu_description

    
    def load_config(self, config_file_name):
        config_file = None
        try:
            config_file = open(config_file_name)
        except IOError, e:
            print 'Could not read configuration from file at:%s\n%s' % (config_file_name, e)
            print 'Initializing it with the default config.'
            subprocess.call(['mkdir', '-p', os.path.dirname(config_file_name)])
            try:
                config_file = open(config_file_name, 'w')
                pprint.pprint(self._default_config, stream=config_file, indent=4)
                config_file.close()
                config_file = None
            except IOError, e:
                print 'Could not write configuration to file at:%s\n%s' % (config_file_name, e)
                        
        config_from_file = {}
        if config_file is not None:
            try:
                config_from_file = eval(config_file.read())
            except Exception, e:
                print 'Could not parse configuration: %s' % e

        self._config = self._default_config.copy()
        self._config.update(config_from_file)

        for launcher in self._config['launchers']:
            launcher['activate'] = self._on_menu_item_launch
            self._launchers.append(launcher)


    def check_online_status(self):
        ping_time_ms = ping(self._config['hosts'][self._next_host], 1.0)
        self._next_host += 1
        self._next_host %= len(self._config['hosts'])

        if ping_time_ms == None:
            self.set_icon('offline')
        elif ping_time_ms > 200:
            self.set_icon('warning')
        else:
            self.set_icon('online')
       
       
    def set_icon(self, status):
        icon_name = '%s-%s.%s' % (self._config.get('icon_theme', 'default'), status, ICON_FORMAT)
        self._indicator.set_icon(icon_name)


    def _on_menu_item_quit(self, menu_item):
        print 'Shutting down'
        self.stop()
        # Shutdown here...
        self._indicator.quit()


    def _on_menu_item_launch(self, menu_item):
        if 'command' in menu_item.user_args:
            subprocess.Popen(menu_item.user_args['command'], shell=True, stdin=None, stdout=None, stderr=None, cwd=os.environ['HOME'])
        else:
            print 'No command found in user_args:', menu_item.user_args



    def run(self):
        while not self._exit:
            self.check_online_status()
            time.sleep(1)


    def stop(self):
        self._exit = True
