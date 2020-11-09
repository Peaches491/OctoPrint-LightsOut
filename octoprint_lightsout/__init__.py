from __future__ import absolute_import

import octoprint.plugin
from octoprint.util import RepeatedTimer


class LightsoutPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):
    def __init__(self):
        self._timer = None

    ##~~ StartupPlugin mixin
    def on_after_startup(self):
        self._logger.info("LightsOut plugin Starting up...")

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(timeout=60, off_gcode="M150 P0")

    def get_timeout_sec(self):
        return int(self._settings.get(["timeout"]))

    def get_off_gcode(self):
        return self._settings.get(["off_gcode"])

    ##~~ EventHandlerPlugin
    def on_event(self, event, payload):
        self._logger.info("LightsOut received event: " + str(event))
        if event in (
            "Startup",
            "SettingsUpdated",
            "PrintFailed",
            "PrintDone",
            "PrintCanceled",
        ):
            self.restart_timer()
        elif event in ("PrintStarted"):
            self.stop_timer()

    def restart_timer(self):
        timeout = self.get_timeout_sec()
        self._logger.info("LightsOut scheduling RepeatedTimer: " + str(timeout))

        self.stop_timer()

        self._timer = RepeatedTimer(
            timeout, self.send_lights_off, run_first=False
        )
        self._timer.start()

    def stop_timer(self):
        if self._timer is not None:
            self._timer.cancel()

    def send_lights_off(self):
        self._logger.info("LightsOut plugin Shutting lights off!")
        off_gcode = self.get_off_gcode()
        self._printer.commands(off_gcode, tags=set(["lightsout"]))

    ##~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/lightsout.js"],
            css=["css/lightsout.css"],
            less=["less/lightsout.less"],
        )

    ##~~ TemplatePlugin mixin
    def get_template_vars(self):
        return dict(
            timeout=self.get_timeout_sec(),
            off_gcode=self.get_off_gcode(),
        )

    def get_template_configs(self):
        return [
            dict(type="navbar", custom_bindings=False),
            dict(type="settings", custom_bindings=False),
        ]

    ##~~ Softwareupdate hook
    def gcode_sent_hook(
        self,
        comm_instance,
        phase,
        cmd,
        cmd_type,
        gcode,
        subcode,
        tags,
        *args,
        **kwargs
    ):
        if self.is_lights_on_gcode(cmd, cmd_type, gcode, tags):
            self._logger.info("LightsOut detected 'ON' GCode: " + cmd)
            self._logger.info("Restarting LightsOut timer")
            self.restart_timer()

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return dict(
            lightsout=dict(
                displayName="LightsOut Plugin",
                displayVersion=self._plugin_version,
                # version check: github repository
                type="github_release",
                user="Peaches491",
                repo="OctoPrint-LightsOut",
                current=self._plugin_version,
                # update method: pip
                pip="https://github.com/Peaches491/OctoPrint-LightsOut/archive/{target_version}.zip",
            )
        )

    def is_lights_on_gcode(self, cmd, cmd_type, gcode, tags):
        if gcode == "M150":
            for token in cmd.split(" "):
                if token.startswith("P"):
                    power_val = int(token.lstrip("P"))
                    if power_val > 0:
                        return True
        return False


__plugin_name__ = "LightsOut"
__plugin_pythoncompat__ = ">=2.7,<4"  # Python 2 or 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = LightsoutPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.gcode_sent_hook,
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
    }
