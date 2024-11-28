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
from gi.repository import Gtk, Pango

from lemma.helpers.observable import Observable
from lemma.infrastructure.layout_info import LayoutInfo


class ToolBar(Observable):

    def __init__(self, workspace, main_window):
        Observable.__init__(self)
        self.toolbar = main_window.toolbar
        self.workspace = workspace

        self.toolbar.toolbar_image.scale.connect('change-value', self.on_image_scale_change_value)

        self.workspace.connect('new_active_document', self.on_new_active_document)
        self.workspace.connect('document_changed', self.on_document_change)

    def on_new_active_document(self, workspace, document=None): self.update()
    def on_document_change(self, workspace, document): self.update()

    def update(self):
        self.update_toolbar()

    def update_toolbar(self):
        document = self.workspace.active_document
        if self.workspace.mode != 'documents' or document == None: return

        selected_nodes = document.ast.get_subtree(*document.cursor.get_state())
        if len(selected_nodes) == 1 and selected_nodes[0].type.is_image():
            image = selected_nodes[0].value

            self.toolbar.mode_stack.set_visible_child_name('image')

            size_string = str(image.get_width()) + ' × ' + str(image.get_height())
            text = image.get_format() + _(' Image') + ' (' + size_string + ')'
            self.toolbar.toolbar_image.status_label.set_text(text)

            max_width = LayoutInfo.get_layout_width()
            max_height = int((max_width / image.get_original_width()) * image.get_original_height())
            max_digits = len(str(max_width)) + len(str(max_height))
            layout = Pango.Layout(self.toolbar.toolbar_image.status_label.get_pango_context())
            layout.set_text(image.get_format() + _(' Image') + ' ( × ' + max_digits * '0' + ')')
            self.toolbar.toolbar_image.status_label.set_size_request(layout.get_extents()[0].width / Pango.SCALE + 20, -1)

            self.toolbar.toolbar_image.scale.set_value(image.get_width())
            self.toolbar.toolbar_image.scale.clear_marks()

            orig_width = image.get_original_width()
            if orig_width > LayoutInfo.get_min_image_size() and orig_width < LayoutInfo.get_layout_width():
                self.toolbar.toolbar_image.scale.add_mark(orig_width, Gtk.PositionType.TOP)
        else:
            self.toolbar.mode_stack.set_visible_child_name('main')

    def on_image_scale_change_value(self, scale, scroll, value):
        self.workspace.active_document.add_command('resize_widget', value)
        return True


