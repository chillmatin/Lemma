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

from lemma.document.ast.node import Node
from lemma.document.ast.link import Link


class Command():

    def __init__(self, target, positions):
        self.target = target
        self.positions = positions
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = False
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()
        self.state['nodes_added'] = []

        document.cursor.set_state(self.positions)
        char_nodes = [node for node in document.ast.get_subtree(*document.cursor.get_state()) if node.is_char()]
        prev_links = []
        for node in char_nodes:
            prev_links.append(node.link)
            node.link = Link(self.target)
        self.state['nodes_and_prev_target'] = list(zip(char_nodes, prev_links))

        document.cursor.set_state(self.state['cursor_state_before'])

    def undo(self, document):
        for item in self.state['nodes_and_prev_target']:
            item[0].link = item[1]

        document.set_scroll_insert_on_screen_after_layout_update()


