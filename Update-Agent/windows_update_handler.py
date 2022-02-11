import logging
from re import sub
from base_classes import UpdateHandler
import subprocess
import sys

class WindowsUpdater(UpdateHandler):
    def __init__(self):
        super()
        logging.info("Windows Updater instantiated")

    def check_for_updates(self):
        logging.info("WindowsUpdater-CheckingForUpdates")
        p = subprocess.Popen(["powershell.exe", "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateupdateSearcher(); $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=0').Updates); $Updates | Select-Object Title"], stdout=sys.stdout)
        p.communicate()
        print(p)


