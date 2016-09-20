
import os
import platform


class Tell:
    def __init__(self, message, title='TV Overlord'):

        enviroment = None

        if platform.system() == 'Linux':
            self.is_notify = False
            desktop = os.environ.get('DESKTOP_SESSION')
            if desktop == 'gnome':
                enviroment = 'gnome'
                # from inside virtualenv the Gnome
                # gi object cannot be loaded
                try:
                    # from gi.repository import GObject
                    import gi
                    gi.require_version('Notify', '0.7')
                    from gi.repository import Notify
                    self.Notify = Notify
                    self.is_notify = True
                except(ImportError):
                    eviroment = None
            elif desktop == 'kde':
                pass
            elif desktop == 'ubuntu':
                pass

        elif platform.system() == 'OSX':
            enviroment = 'osx'
            from Foundation import NSUserNotification
            from Foundation import NSUserNotificationCenter
            from Foundation import NSUserNotificationDefaultSoundName

        if enviroment == 'osx':
            self.osx_message(title, message)
        elif enviroment == 'gnome':
            self.gnome_message(title, message)
        elif enviroment == 'kde':
            self.kde_message(title, message)
        elif enviroment == 'ubuntu':
            self.ubuntu_message(title, message)
        elif enviroment == 'windows':
            self.windows_notify(title, message)

    def gnome_message(self, title, message):
        if not self.is_notify:
            return
        self.Notify.init('TV')
        icon = ''
        n = self.Notify.Notification.new(title, message, icon)
        n.show()

    def osx_message(self, title, message):
        # based on:
        # https://gist.github.com/baliw/4020619
        # http://stackoverflow.com/questions/17651017/python-post-osx-notification
        notification = NSUserNotification.alloc().init()
        notification.setTitle_(title)
        notification.setInformativeText_(message)

        center = NSUserNotificationCenter.defaultUserNotificationCenter()
        center.deliverNotification_(notification)

    def kde_message(self, title, message):
        # http://stackoverflow.com/questions/4107743/updating-notification-using-knotify
        pass

    def ubuntu_message(self, title, message):
        pass

    def windows_notify(self, title, message):
        pass
