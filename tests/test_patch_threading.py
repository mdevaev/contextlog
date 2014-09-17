import threading

import contextlog


# =====
def test_patch_threading():
    try:
        orig_thread_start = threading.Thread.start
        orig_thread_bootstrap = threading.Thread._bootstrap  # pylint: disable=protected-access

        contextlog.get_logger(foo="bar")

        class TestThread(threading.Thread):
            def __init__(self):
                threading.Thread.__init__(self)
                self.context = None

            def run(self):
                self.context = contextlog.get_logger().get_context()

        contextlog.patch_threading()

        thread = TestThread()
        thread.start()
        thread.join()

        assert thread.context == {"foo": "bar"}

    finally:
        threading.Thread.start = orig_thread_start
        threading.Thread._bootstrap = orig_thread_bootstrap  # pylint: disable=protected-access
