import logging
from base_classes import UpdateHandler


class WindowsUpdater(UpdateHandler):
    def __init__(self):
        super()
        logging.info("Windows Updater instantiated")

    def check_for_updates(self):
        logging.info("WindowsUpdater-CheckingForUpdates")
        """
        $UpdateSession = New-Object -ComObject Microsoft.Update.Session
        $UpdateSearcher = $UpdateSession.CreateupdateSearcher()
        $Updates = @($UpdateSearcher.Search("IsHidden=0 and IsInstalled=0").Updates)
        $Updates | Select-Object Title
        """
