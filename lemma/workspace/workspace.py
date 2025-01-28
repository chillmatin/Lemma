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

from operator import attrgetter

from lemma.helpers.observable import Observable
from lemma.workspace.document_history import DocumentHistory


class Workspace(Observable):

    def __init__(self):
        Observable.__init__(self)

        self.active_document = None
        self.mode = 'documents'

        self.max_document_id = 0
        self.documents = list()
        self.documents_by_id = dict()
        self.active_document = None

        self.history = DocumentHistory(self)
        self.links_by_target = dict()

    def add(self, document):
        self.max_document_id = max(self.max_document_id, document.id)
        self.documents.append(document)
        self.documents.sort(key=attrgetter('last_modified'), reverse=True)
        self.documents_by_id[document.id] = document
        self.update_links()
        self.add_change_code('new_document', document)
        self.add_change_code('changed')

    def delete_document(self, document):
        if document == None: return
        if document == self.active_document:
            self.set_active_document(self.history.get_next_in_line(document))

        self.history.delete(document)
        self.documents.remove(document)
        self.update_links()
        self.add_change_code('document_removed', document)
        self.add_change_code('changed')

    def get_by_id(self, id):
        if id in self.documents_by_id:
            return self.documents_by_id[id]
        return None

    def get_by_title(self, title):
        for document in self.documents:
            if title == document.title:
                return document

    def get_active_document(self):
        return self.active_document

    def enter_draft_mode(self):
        self.mode = 'draft'
        self.add_change_code('mode_set')

        self.history.activate_document(None)

    def leave_draft_mode(self):
        self.mode = 'documents'
        self.add_change_code('mode_set')

        self.history.activate_document(self.active_document)

    def set_active_document(self, document, update_history=True):
        self.mode = 'documents'
        self.add_change_code('mode_set')

        if self.active_document != None: self.active_document.disconnect('changed', self.on_document_change)
        self.active_document = document
        if document != None: self.active_document.connect('changed', self.on_document_change)

        if update_history and document != None:
            self.history.add(document)
        self.history.activate_document(document)

        self.add_change_code('new_active_document', document)

    def get_new_document_id(self):
        return self.max_document_id + 1

    def on_document_change(self, document):
        self.update_links()
        self.documents.sort(key=attrgetter('last_modified'), reverse=True)
        self.add_change_code('document_changed', document)

    def update_links(self):
        links_by_target = dict()
        for document in self.documents:
            links = self.find_links(document.ast)
            for link in links:
                if link.target not in links_by_target:
                    links_by_target[link.target] = set()
                links_by_target[link.target].add(document.title)

        self.links_by_target = links_by_target

    def find_links(self, node):
        links = []
        if node.link != None:
            links.append(node.link)
        for child in node:
            links += self.find_links(child)
        return links


