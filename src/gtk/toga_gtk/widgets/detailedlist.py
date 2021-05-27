from ..libs import Gtk, GLib
from .base import Widget
from .internal.rows import TextIconRow
from .internal.buttons import RefreshButton, ScrollButton
from .internal.sourcelistmodel import SourceListModel


class DetailedList(Widget):
    """
    Gtk DetailedList implementation.
    Gtk.ListBox inside a Gtk.ScrolledWindow.
    """
    def create(self):
        self._on_refresh_handler = None
        self._on_select_handler = None
        self._on_delete_handler = None

        self.list_box = Gtk.ListBox()

        self.list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)

        self.store = SourceListModel(TextIconRow, self.interface.factory)
        self.store.bind_to_list(self.list_box)
        self.store.set_on_select(self._on_select)

        self.scrolled_window = Gtk.ScrolledWindow()

        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.set_min_content_width(self.interface.MIN_WIDTH)
        self.scrolled_window.set_min_content_height(self.interface.MIN_HEIGHT)

        self.scrolled_window.add(self.list_box)

        self.refresh_button = RefreshButton(self.scrolled_window.get_vadjustment())
        self.refresh_button.set_on_refresh(self._on_refresh)

        self.scroll_button = ScrollButton(self.scrolled_window.get_vadjustment())
        self.scroll_button.set_scroll(lambda: self.scroll_to_row(-1))
        
        self.native = Gtk.Overlay()
        self.native.add_overlay(self.scrolled_window)

        self.refresh_button.overlay_over(self.native)
        self.scroll_button.overlay_over(self.native)

        self.native.interface = self.interface
      
    def change_source(self, source: 'ListSource'):
        self.store.change_source(source)

        # We have to wait until the rows are actually added decide how to position the
        # refresh button
        GLib.idle_add(lambda: not self._changed())

    def insert(self, index: int, item: 'Row'):
        self.store.insert(index, item)
        self.list_box.show_all()
        self._changed()

    def change(self, item: 'Row'):
        self.store.change(item)
        self._changed()
        
    def remove(self, item: 'Row', index: int):
        self.store.remove(item, index)
        self._changed()
        self._on_delete(item)
        
    def clear(self):
        self.store.remove_all()
        self._changed()

    def get_selection(self):
        return self.store.get_selection()

    def scroll_to_row(self, row: int):
        self.store.scroll_to_row(row)

    def set_on_refresh(self, handler: callable):
        self._on_refresh_handler = handler

    def set_on_select(self, handler: callable):
        self._on_select_handler = handler

    def set_on_delete(self, handler: callable):
        self._on_delete_handler = handler

    def after_on_refresh(self):
        # No special handling required
        pass

    def _on_refresh(self):
        if self._on_refresh_handler is not None:
            self._on_refresh_handler(self.interface)

    def _on_select(self, row: 'Row'):
        if self._on_select_handler is not None:
            self._on_select_handler(self.interface, row)

    def _on_delete(self, row: 'Row'):
        if self._on_delete_handler is not None:
            self._on_delete_handler(self.interface, row)

    def _changed(self):
        self.refresh_button.list_changed()
        self.scroll_button.list_changed()
        return True

