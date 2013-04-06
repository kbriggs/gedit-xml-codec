# -*- coding: utf8 -*-
# A utility for XML-encoding/decoding blocks of text
#
# Copyright © 2013 Kieron Briggs <https://github.com/kbriggs>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from gi.repository import GObject, Gtk, Gedit

UI_XML = """<ui>
<menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_3">
        <menuitem name="XmlDecodeAction" action="XmlDecodeAction"/>
        <menuitem name="XmlEncodeAction" action="XmlEncodeAction"/>
      </placeholder>
    </menu>
</menubar>
</ui>"""

class XmlCodecPlugin(GObject.Object, Gedit.WindowActivatable):
    __gtype_name__ = "XmlCodecPlugin"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._add_menu()

    def do_deactive(self):
        self._rem_menu()

    def do_update_state(self):
        pass

    def _add_menu(self):
        manager = self.window.get_ui_manager()
        self._actions = Gtk.ActionGroup("XmlCodecActions")
        self._actions.add_actions([
            ('XmlDecodeAction', Gtk.STOCK_INFO, "XML _Decode", 
                None, "XML-decode the current selection", 
                self.on_xmldecode_action_activate),
            ('XmlEncodeAction', Gtk.STOCK_INFO, "XML _Encode", 
                None, "XML-encode the current selection", 
                self.on_xmlencode_action_activate),
        ])
        manager.insert_action_group(self._actions)
        self._ui_merge_id = manager.add_ui_from_string(UI_XML)
        manager.ensure_update()

    def _rem_menu(self):
        manager = self.window.get_ui_manager()
        manager.remove_ui(self._ui_merge_id)
        manager.remove_action_group(self._actions)
        manager.ensure_update()

    def on_xmldecode_action_activate(self, action, data=None):
        bounds = self.get_bounds()
        if bounds:
            new_text = self.xml_decode(self.get_text(bounds))
            if new_text:
                self.set_text(bounds, new_text)

    def on_xmlencode_action_activate(self, action, data=None):
        bounds = self.get_bounds()
        if bounds:
            new_text = self.xml_encode(self.get_text(bounds))
            if new_text:
                self.set_text(bounds, new_text)

    def get_bounds(self):
        view = self.window.get_active_view()
        if view:
            bounds = view.get_buffer().get_selection_bounds()
            if not bounds:
                bounds = view.get_buffer().get_bounds()
            return bounds
        else:
            return None

    def get_text(self, bounds):
        view = self.window.get_active_view()
        if view:
            return view.get_buffer().get_text(bounds[0], bounds[1], True)
        else:
            return None

    def set_text(self, bounds, text):
        view = self.window.get_active_view()
        if view:
            view.get_buffer().delete(*bounds)
            view.get_buffer().insert(bounds[0], text)

    # we use the 'wrap in a dummy element' approach to encode/decode
    def xml_decode(self, text):
        from xml.dom.minidom import parseString
        d = parseString("<x>%s</x>" % (text))
        return d.documentElement.firstChild.data

    def xml_encode(self, text):
        from xml.dom.minidom import Text, Element
        t = Text()
        t.data = text
        e = Element('x')
        e.appendChild(t)
        return e.toxml()[3:-4]

