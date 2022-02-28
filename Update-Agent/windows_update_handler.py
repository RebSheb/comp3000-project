import logging
from re import sub
from typing import Text
from base_classes import UpdateHandler
from uuid import getnode as get_mac
import subprocess
import sys


class WindowsUpdater(UpdateHandler):
    def __init__(self, api_endpoint, api_port):
        super().__init__(api_endpoint, api_port)
        logging.info("Windows Updater instantiated")

    def check_for_updates(self):
        logging.info("WindowsUpdater-CheckingForUpdates")
        p = subprocess.Popen(
            ["powershell.exe", "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateupdateSearcher(); $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=0').Updates); $Updates | ForEach-Object -Begin $null -Process { $_.Title ; $_.Description ; $_.KBArticleIDs }"], stdout=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = p.communicate()
        # Remove Windows return carriages and split into a list from \n's
        stdout = stdout.strip("\r").split("\n")
        # Remove the erronous newline which Powershell seems to enjoy putting in
        stdout = stdout[:-1]
        # Split every 3rd element so we get a list of lists for each update
        composite_list = [stdout[x:x+3] for x in range(0, len(stdout), 3)]

        post_data = []
        for update in composite_list:
            post_data.append({
                "PkgName": update[0],
                "PkgDescription": update[1],
                "PkgLatest": update[2]
            })

        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))

        self.post_data(mac, post_data)
