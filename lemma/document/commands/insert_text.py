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

    def __init__(self, text, link_target=None, tags=set()):
        self.is_undo_checkpoint = True
        self.update_implicit_x_position = True
        self.text = text
        self.link_target = link_target
        self.tags = tags
        self.state = dict()

    def run(self, document):
        self.state['cursor_state_before'] = document.cursor.get_state()
        self.state['nodes_added'] = []

        insert = document.cursor.get_insert_node()
        paragraph_style_at_cursor = insert.paragraph_style

        for char in self.text:
            character = Node('char', char)
            character.tags = self.tags.copy()
            character.paragraph_style = paragraph_style_at_cursor
            if self.link_target != None:
                character.link = Link(self.link_target)
            insert.parent.insert_before(insert, character)
            self.state['nodes_added'].append(character)

        self.is_undo_checkpoint = (len(self.state['nodes_added']) > 0 or len(self.state['deleted_nodes']) > 0 )
        document.set_scroll_insert_on_screen_after_layout_update()

    def undo(self, document):
        for node in self.state['nodes_added']:
            node.remove_from_parent()
        document.cursor.set_state(self.state['cursor_state_before'])
        document.set_scroll_insert_on_screen_after_layout_update()


