#!/usr/bin/env python

import os, sys, signal
from indicator_update_thread import IndicatorUpdateThread

try:
    from gtk_indicator_menu import GtkIndicatorMenu as IndicatorMenu
except:
    from qt_indicator_menu import QtIndicatorMenu as IndicatorMenu

def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    package_dir = os.path.abspath(os.path.dirname(__file__))
    indicator = IndicatorMenu('online-status-indicator', 'default-unknown.svg', package_dir + '/icons')
    indicatorUpdateThread = IndicatorUpdateThread(indicator)
    indicatorUpdateThread.start()
    try:
        sys.exit(indicator.main())
    except KeyboardInterrupt:
        indicatorUpdateThread.stop()
        sys.exit(0)

if __name__ == '__main__':
    main()
