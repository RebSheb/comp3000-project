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
        # p = subprocess.Popen(
        #    ["powershell.exe", "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateupdateSearcher(); $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=0').Updates); $Updates | ForEach-Object -Begin $null -Process { $_.Title ; $_.Description ; $_.KBArticleIDs }"], stdout=subprocess.PIPE, universal_newlines=True)
        eap = subprocess.check_output(
            ["powershell.exe",
                "$UpdateSession = New-Object -ComObject Microsoft.Update.Session; $UpdateSearcher = $UpdateSession.CreateupdateSearcher(); $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=0').Updates); $Updates | ForEach-Object -Begin $null -Process { $_.Title ; $_.Description ; $_.KBArticleIDs }"],
            universal_newlines=True)

        # stdout, stderr = p.communicate()
        # Remove Windows return carriages and split into a list from \n's
        # stdout = stdout.strip("\r").split("\n")
        eap = eap.strip("\r").split("\n")
        # Remove the erronous newline which Powershell seems to enjoy putting in
        # stdout = stdout[:-1]
        eap = eap[:-1]
        # Split every 3rd element so we get a list of lists for each update
        # composite_list = [stdout[x:x+3] for x in range(0, len(stdout), 3)]
        composite_list = [eap[x:x+3] for x in range(0, len(eap), 3)]

        post_data = []
        for update in composite_list:
            post_data.append({
                "PkgName": update[0],
                "PkgDescription": update[1],
                "PkgVersion": "",
                "PkgLatest": update[2]
            })

        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        post_data = post_data + self.enumerate_installed_applications()

        self.post_data(mac.lower(), post_data)

    def enumerate_installed_applications(self):
        installed_apps = subprocess.check_output(
            ["powershell.exe", "foreach($pkg in (Get-WmiObject -Class Win32_Product | Select-Object Name,Version)) { if ($pkg.Name) {$pkg.Name + ',' +  $pkg.Version} }"], universal_newlines=True)
        installed_apps = installed_apps.split("\n")[:-1]

        app_data = []
        for app in installed_apps:
            app_info = app.split(",")
            app_data.append({
                "PkgName": app_info[0],
                "PkgDescription": "",
                "PkgVersion": app_info[1],
                "PkgLatest": ""
            })

        return app_data
