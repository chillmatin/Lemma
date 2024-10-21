#!/usr/bin/env python3
# coding: utf-8

# Copyright (C) 2017-present Robert Griesel
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk
from gi.repository import GLib
import os.path
import pickle

from lemma.helpers.observable import Observable


class Settings(Observable):
    ''' Settings controller for saving application state. '''

    def __init__(self, pathname):
        Observable.__init__(self)

        self.gtksettings = Gtk.Settings.get_default()

        self.pathname = pathname

        self.data = dict()
        self.defaults = dict()
        self.set_defaults()

        if not self.unpickle():
            self.data = self.defaults
            self.pickle()

        # load gsettings schema concerning application menu / window decorations
        self.button_layout = self.gtksettings.get_property('gtk-decoration-layout')

    def set_defaults(self):
        self.defaults['window_state'] = dict()
        self.defaults['window_state']['width'] = 1020
        self.defaults['window_state']['height'] = 550
        self.defaults['window_state']['is_maximized'] = False
        self.defaults['window_state']['sidebar_position'] = 250
        self.defaults['window_state']['show_tools_sidebar'] = False
        self.defaults['window_state']['tools_sidebar_position'] = -1
        self.defaults['window_state']['show_backlinks'] = False
        self.defaults['window_state']['navbar_paned_position'] = -1

        self.defaults['app_state'] = dict()
        self.defaults['app_state']['last_export_folder'] = None
        self.defaults['app_state']['last_bulk_export_folder'] = None
        self.defaults['app_state']['last_import_folder'] = None

        self.defaults['preferences'] = dict()
        self.defaults['preferences']['color_scheme'] = 'default'

    def get_value(self, section, item):
        try: value = self.data[section][item]
        except KeyError:
            value = self.defaults[section][item]
            self.set_value(section, item, value)
        return value

    def set_value(self, section, item, value):
        try: section_dict = self.data[section]
        except KeyError:
            section_dict = dict()
            self.data[section] = section_dict
        section_dict[item] = value
        self.add_change_code('settings_changed', (section, item, value))

    def unpickle(self):
        ''' Load settings from home folder. '''

        # create folder if it does not exist
        if not os.path.isdir(self.pathname):
            os.makedirs(self.pathname)
        
        try: filehandle = open(os.path.join(self.pathname, 'settings.pickle'), 'rb')
        except IOError: return False
        else:
            try: self.data = pickle.load(filehandle)
            except EOFError: False
            
        return True

    def pickle(self):
        ''' Save settings in home folder. '''

        try: filehandle = open(os.path.join(self.pathname, 'settings.pickle'), 'wb')
        except IOError: return False
        else: pickle.dump(self.data, filehandle)


