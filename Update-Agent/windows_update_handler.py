import logging
from re import sub
from typing import Text
from base_classes import UpdateHandler
from uuid import getnode as get_mac
import subprocess
import sys
import requests
import json


class WindowsUpdater(UpdateHandler):
    def __init__(self, api_endpoint, api_port):
        super().__init__(api_endpoint, api_port)
        logging.info("Windows Updater instantiated")

    def check_for_updates(self):
        logging.info("WindowsUpdater-CheckingForUpdates")

        powershell_output = subprocess.check_output(
            ["powershell.exe",
                """$UpdateSession = New-Object -ComObject Microsoft.Update.Session;
                 $UpdateSearcher = $UpdateSession.CreateupdateSearcher();
                 $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=0').Updates);
                 $Updates | ForEach-Object -Begin $null -Process { $_.Title ; $_.Description ; $_.KBArticleIDs }"""
             ],
            universal_newlines=True, creationflags=subprocess.SW_HIDE, shell=True)

        # Remove Windows return carriages and split into a list from \n's
        # stdout = stdout.strip("\r").split("\n")
        powershell_output = powershell_output.strip("\r").split("\n")
        # Remove the erronous newline which Powershell seems to enjoy putting in
        # stdout = stdout[:-1]
        powershell_output = powershell_output[:-1]
        # Split every 3rd element so we get a list of lists for each update
        # composite_list = [stdout[x:x+3] for x in range(0, len(stdout), 3)]
        composite_list = [powershell_output[x:x+3]
                          for x in range(0, len(powershell_output), 3)]

        post_data = []
        for update in composite_list:
            pkg_data = {"PkgName": None, "PkgDescription": None,
                        "PkgVersion": None, "PkgLatest": None, "is_installed": 0}

            pkg_data["PkgName"] = update[0]
            try:
                pkg_data["PkgDescription"] = update[1]
            except IndexError:
                logging.warn(
                    "Update {} has no Description field!".format(update[0]))
                pass

            try:
                pkg_data["PkgLatest"] = update[2]
            except IndexError:
                logging.warn(
                    "Update {} has no Version field, substituting 1!".format(update[0]))
                pkg_data["PkgLatest"] = "1"
                pass

            post_data.append(pkg_data)

        mac = get_mac()
        mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
        post_data = post_data + self.enumerate_installed_applications() + \
            self.enumerate_installed_updates()

        self.post_data(mac.lower(), post_data)

    def enumerate_installed_updates(self):
        logging.info("WindowsUpdater-EnumerateInstalledUpdates")
        powershell_output = subprocess.check_output(
            ["powershell.exe",
                """$UpdateSession = New-Object -ComObject Microsoft.Update.Session;
                 $UpdateSearcher = $UpdateSession.CreateupdateSearcher();
                 $Updates = @($UpdateSearcher.Search('IsHidden=0 and IsInstalled=1').Updates);
                 $Updates | ForEach-Object -Begin $null -Process { $_.Title ; $_.Description ; $_.KBArticleIDs }"""
             ],
            universal_newlines=True, creationflags=subprocess.SW_HIDE)

        # Remove Windows return carriages and split into a list from \n's
        # stdout = stdout.strip("\r").split("\n")
        powershell_output = powershell_output.strip("\r").split("\n")
        # Remove the erronous newline which Powershell seems to enjoy putting in
        # stdout = stdout[:-1]
        powershell_output = powershell_output[:-1]
        # Split every 3rd element so we get a list of lists for each update
        # composite_list = [stdout[x:x+3] for x in range(0, len(stdout), 3)]
        composite_list = [powershell_output[x:x+3]
                          for x in range(0, len(powershell_output), 3)]

        post_data = []
        for update in composite_list:
            pkg_data = {"PkgName": None, "PkgDescription": None,
                        "PkgVersion": None, "PkgLatest": "", "is_installed": 1}

            pkg_data["PkgName"] = update[0]
            try:
                pkg_data["PkgDescription"] = update[1]
            except IndexError:
                logging.warn(
                    "Update {} has no Description field!".format(update[0]))
                pass

            try:
                pkg_data["PkgVersion"] = update[2]
            except IndexError:
                logging.warn(
                    "Update {} has no Version field, substituting 1!".format(update[0]))
                pkg_data["PkgVersion"] = "1"
                pass

            post_data.append(pkg_data)
        logging.info("WindowsUpdater-EnumerateInstalledUpdates finished")
        return post_data

    def enumerate_installed_applications(self):
        installed_apps = subprocess.check_output(
            ["powershell.exe", "foreach($pkg in (Get-WmiObject -Class Win32_Product | Select-Object Name,Version)) { if ($pkg.Name) {$pkg.Name + ',' +  $pkg.Version} }"], universal_newlines=True, creationflags=subprocess.SW_HIDE, shell=True)
        installed_apps = installed_apps.split("\n")[:-1]

        app_data = []
        for app in installed_apps:
            pre_app_data = {"PkgName": None, "PkgDescription": None,
                            "PkgVersion": None, "PkgLatest": "", "is_installed": None}
            app_info = app.split(",")
            pre_app_data["PkgName"] = app_info[0]
            pre_app_data["PkgVersion"] = app_info[1]
            app_data.append(pre_app_data)

        return app_data

    def perform_update(self):
        logging.info("WindowsUpdater-PerformUpdate - It's time to update!")
        ps_update_command = """
            #Search for relevant updates.

            $Searcher = New-Object -ComObject Microsoft.Update.Searcher

            $SearchResult = $Searcher.Search("IsInstalled=0").Updates


            #Download updates.

            $Session = New-Object -ComObject Microsoft.Update.Session

            $Downloader = $Session.CreateUpdateDownloader()

            $Downloader.Updates = $SearchResult

            $Downloader.Download()


            $Installer = New-Object -ComObject Microsoft.Update.Installer

            $Installer.Updates = $SearchResult

            $Result = $Installer.Install()

            Write-Output $Result
        """

        update_result = subprocess.check_output(
            ["powershell.exe", ps_update_command], universal_newlines=True)
        logging.info(
            "WindowsUpdater-PerformUpdate - Subprocess finished updates; result: {}".format(update_result))

    def post_data(self, mac_address: str = None, data_to_post: list = None):
        if data_to_post is None:
            return ("Data to post is None!", False)
        if mac_address is None:
            return ("Mac Address is None!", False)

        # Format of the list should be like this for Linux
        # [ {"PkgName": "python3", "PkgVersion": "3.9.7", "PkgLatest": "3.9.8"} ]
        # For Windows
        # [ {"PkgName": "Security Intelligence Update for Microsoft Defender Antivirus - KB2267602 (Version 1.359.191.0)", "PkgLatest": "3.9.8", "PkgDescription": "Blah Blah"} ]
        self.mac = mac_address
        data = {
            "mac_address": mac_address,
            "data": data_to_post
        }
        data = json.dumps(data)
        try:
            if len(data_to_post) > 0:
                requests.post(str(self.api_endpoint) + ":" +
                              str(self.api_port) + "/agent/windows_post_data", json=data)
        except Exception as error:
            logging.error(error)
            return (str(error), False)
