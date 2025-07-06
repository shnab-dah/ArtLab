import sys
import time
import serial
import serial.tools.list_ports
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QMessageBox, QComboBox, QHBoxLayout
)


class MSICaptureApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MSI Capture - digiCamControl + COM Select")
        self.resize(400, 200)

        self.wavelengths = [365, 395, 425, 445, 460, 620, 600, 620, 660, 685, 735, 850, 885, 940]
        self.num_lights = len(self.wavelengths)

        self.dcc_path = r"C:\Program Files (x86)\digiCamControl\CameraControlRemoteCmd.exe"
        self.light_on_delay = 0.3
        self.post_capture_delay = 1.5  # <- Keep flash ON during this delay
        self.retry_delay = 1.0
        self.max_retries = 5

        self.serial_port = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # COM port selection
        port_row = QHBoxLayout()
        port_row.addWidget(QLabel("Select COM Port:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(self.get_serial_ports())
        port_row.addWidget(self.port_combo)
        layout.addLayout(port_row)

        # Status label
        self.status_label = QLabel("Ready to capture MSI images.")
        layout.addWidget(self.status_label)

        # Start capture button
        self.capture_button = QPushButton("Start Capture")
        self.capture_button.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_button)

        self.setLayout(layout)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def send_command(self, func, light):
        if not self.serial_port or not self.serial_port.is_open:
            raise Exception("Serial port not open")
        cmd = f"<{func},{light},0,0,0>"
        self.serial_port.write(cmd.encode())

    def trigger_capture(self):
        for attempt in range(1, self.max_retries + 1):
            result = subprocess.run(
                f'"{self.dcc_path}" /c "capture"',
                shell=True,
                capture_output=True,
                text=True
            )
            output = (result.stdout + result.stderr).lower()

            if "device is busy" in output:
                self.status_label.setText(f"Device busy, retrying {attempt}/{self.max_retries}...")
                QApplication.processEvents()
                time.sleep(self.retry_delay)
            elif result.returncode == 0:
                return True
            else:
                self.status_label.setText(f"Capture error: {output}")
                QApplication.processEvents()
                return False

        self.status_label.setText("Failed to capture: device remained busy after retries.")
        QApplication.processEvents()
        return False

    def start_capture(self):
        selected_port = self.port_combo.currentText()

        if not selected_port:
            QMessageBox.warning(self, "No Port Selected", "Please select a COM port.")
            return

        try:
            self.serial_port = serial.Serial(selected_port, 9600, timeout=1)
            time.sleep(2)
        except Exception as e:
            QMessageBox.critical(self, "Serial Error", f"Failed to open {selected_port}:\n{e}")
            return

        self.capture_button.setEnabled(False)

        try:
            for i, wl in enumerate(self.wavelengths):
                self.status_label.setText(f"Lighting LED {i+1}/{self.num_lights} ({wl}nm)...")
                QApplication.processEvents()

                self.send_command(2, i)  # LED ON
                time.sleep(self.light_on_delay)

                success = self.trigger_capture()

                time.sleep(self.post_capture_delay)  # <- Keep LED ON during exposure/write

                self.send_command(3, i)  # LED OFF

                if not success:
                    raise Exception(f"Failed to capture image for light {i+1} ({wl}nm).")

            self.status_label.setText("Capture complete.")
            QMessageBox.information(self, "Done", "Image sequence captured successfully.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        finally:
            self.capture_button.setEnabled(True)
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MSICaptureApp()
    window.show()
    sys.exit(app.exec_())
