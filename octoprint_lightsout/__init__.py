# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin


class LightsoutPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.TemplatePlugin,
):

    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
        )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/lightsout.js"],
            css=["css/lightsout.css"],
            less=["less/lightsout.less"],
        )

    ##~~ Softwareupdate hook

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


__plugin_name__ = "LightsOut Plugin"

__plugin_pythoncompat__ = ">=3,<4"  # only python 3


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = LightsoutPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }
