import unittest
import threading
import time
import tkinter as tk

from page_text_writer_app import PageTextWriterApp
from handwriting.path.curve.point import Point


class TestAnchorPoints(unittest.TestCase):

    def setUp(self):
        self.app_root = None
        self.app: PageTextWriterApp = None
        self.app_mutex = threading.Lock()
        self.app_mutex.acquire()

        def start_app(test):
            test.app_root = tk.Tk()
            test.app = PageTextWriterApp(test.app_root)
            test.app_mutex.release()
            test.app_root.mainloop()

        self.main_thread = threading.Thread(target=start_app, args=(self,))
        self.main_thread.start()
        self.app_mutex.acquire()
        time.sleep(0.01)

    def test_anchor_draw(self):

        self.app.mouse_position = Point(128, 128)
        self.app.handle_edit_page_points()
        self.assertEqual(self.app.mouse_position,
                         self.app.pages_manager.anchor_manager.get_current_point())

    def test_draw_multiple_anchors(self):
        self.app.pages_manager.current_page().lines_points = [
            [Point(100, 150), Point(120, 80), Point(116, 90)]
        ]
        self.app.handle_edit_page_points()

        self.app.mouse_position = Point(128, 128)
        self.assertEqual(self.app.mouse_position,
                         self.app.pages_manager.anchor_manager.get_current_point())

    def tearDown(self):
        self.app_root.quit()
        self.main_thread.join()
