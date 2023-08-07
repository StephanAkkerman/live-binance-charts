import sys
import ctypes
import finplot as fplt
from PyQt6.QtWidgets import QGraphicsView, QGridLayout, QApplication
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtCore import QCoreApplication


# Local imports
import config
import vars
from binance_api import twm

from gui import create_intial_GUI
from plot import realtime_update_plot


class CustomGraphicsView(QGraphicsView):
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle the close event of the main window."""

        # Stop the binance sockets
        twm.stop()

        # Ensure the application quits properly
        QCoreApplication.quit()


if __name__ == "__main__":
    # Make PyQt6 related stuff
    app = QApplication([])
    vars.window = CustomGraphicsView()

    # Layout for the charts
    vars.global_layout = QGridLayout()
    vars.window.setLayout(vars.global_layout)
    vars.window.setWindowTitle("Charts")

    # Background color surrounding the plots
    vars.window.setStyleSheet("background-color:" + fplt.background)
    width = ctypes.windll.user32.GetSystemMetrics(0)
    height = ctypes.windll.user32.GetSystemMetrics(1)
    vars.window.resize(int(width * 0.7), int(height * 0.7))

    # Finplot requres this property
    vars.window.axs = []
    fplt.autoviewrestore()

    # Start binance sockets
    twm.start()

    # Create the 4 plots + control panel
    create_intial_GUI()

    # Gets called every 5 sec
    fplt.timer_callback(realtime_update_plot, 5)

    # prepares plots when they're all set up
    fplt.show(qt_exec=False)
    vars.window.show()
    sys.exit(app.exec())
