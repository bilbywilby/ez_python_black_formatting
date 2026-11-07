import os
import sys
import subprocess
import traceback
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QProgressBar, QComboBox, QMessageBox, QDialog, QLineEdit, QPushButton, QFormLayout


class VideoOptimizationApp(QWidget):

    def __init__(self):
        super().__init__()

        # Variables to store the user's selections
        self.directory_paths = []
        self.output_format = ".mp4"
        self.file_prefix = "video_"
        self.replace_spaces = True
        self.optimize_threads = []
        self.preview_thread = None

        # Set up the layout
        self.setup_layout()

        # Set the window properties
        self.setWindowTitle('Video Optimization App')
        self.setFixedSize(800, 400)
        self.show()

    def setup_layout(self):
        # Set up the widgets
        label1 = QLabel(
            "1. Choose a directory/directories containing video files to optimize:")
        self.directory_label = QLabel()
        self.directory_label.setFixedHeight(20)
        select_directory_button = QPushButton("Select Directory")
        select_directory_button.clicked.connect(self.add_directory)

        label2 = QLabel("2. Choose an output format for the videos:")
        self.format_combobox = QComboBox()
        self.format_combobox.addItem(".mp4")
        self.format_combobox.addItem(".avi")
        self.format_combobox.addItem(".mov")
        self.format_combobox.addItem(".wmv")
        self.format_combobox.addItem(".flv")
        self.format_combobox.addItem(".mkv")
        self.format_combobox.setCurrentIndex(0)
        self.format_combobox.currentIndexChanged.connect(
            self.update_output_format)

        label3 = QLabel("3. Choose a prefix for the renamed files:")
        self.prefix_label = QLabel()
        self.prefix_label.setFixedHeight(20)
        self.prefix_edit = QLineEdit("video_")
        self.prefix_edit.setFixedWidth(80)
        self.prefix_edit.setFixedHeight(20)
        self.prefix_edit.setAlignment(Qt.AlignCenter)
        self.prefix_edit.setStyleSheet("QLineEdit { border: 1px solid gray }")
        self.prefix_edit.textChanged.connect(self.update_file_prefix)

        label4 = QLabel("4. Replace spaces in file names with underscores:")
        self.checkBox = QPushButton("Yes")
        self.checkBox.setCheckable(True)
        self.checkBox.setChecked(True)
        self.checkBox.toggled.connect(self.update_replace_spaces)

        self.optimize_button = QPushButton("Optimize Videos")
        self.optimize_button.setEnabled(False)
        self.optimize_button.clicked.connect(self.start_optimization)

        self.preview_button = QPushButton("Preview")
        self.preview_button.setEnabled(False)
        self.preview_button.clicked.connect(self.start_preview)

        self.status_label = QLabel()
        self.status_label.setFixedHeight(20)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        # Set up the layout
        directory_layout = QHBoxLayout()
        directory_layout.addWidget(label1)
        directory_layout.addWidget(self.directory_label)
        directory_layout.addWidget(select_directory_button)

        format_layout = QHBoxLayout()
        format_layout.addWidget(label2)
        format_layout.addWidget(self.format_combobox)

        prefix_layout = QHBoxLayout()
        prefix_layout.addWidget(label3)
        prefix_layout.addWidget(self.prefix_label)
        prefix_layout.addWidget(self.prefix_edit)

        replace_spaces_layout = QHBoxLayout()
        replace_spaces_layout.addWidget(label4)
        replace_spaces_layout.addWidget(self.checkBox)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.preview_button)
        button_layout.addWidget(self.optimize_button)
        button_layout.addStretch()

        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)

        progress_layout = QHBoxLayout()
        progress_layout.addWidget(self.progress_bar)

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addLayout(directory_layout)
        layout.addLayout(format_layout)
        layout.addLayout(prefix_layout)
        layout.addLayout(replace_spaces_layout)
        layout.addStretch()
        layout.addLayout(button_layout)
        layout.addLayout(status_layout)
        layout.addLayout(progress_layout)

        # Set the layout
        self.setLayout(layout)

    def add_directory(self):
        """Open a file dialog to select a directory."""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory and directory not in self.directory_paths:
            self.directory_paths.append(directory)
            self.update_directory_label()

            if not self.optimize_thread_exists():
                self.optimize_button.setEnabled(True)

    def update_output_format(self, index):
        """Update the output file format based on the user's selection."""
        self.output_format = self.format_combobox.currentText()

    def update_file_prefix(self, text):
        """Update the file prefix based on user input."""
        self.file_prefix = text
        self.prefix_label.setText(self.file_prefix)

    def update_replace_spaces(self):
        """Update the replace_spaces variable based on the user's selection."""
        self.replace_spaces = self.checkBox.isChecked()

    def update_directory_label(self):
        """Update the directory path label to show selected directories."""
        if len(self.directory_paths) == 1:
            self.directory_label.setText(self.directory_paths[0])
        else:
            self.directory_label.setText(
                f"{len(self.directory_paths)} directories selected")

    def start_optimization(self):
        """Start the optimization process in a new thread."""
        self.status_label.setText("Optimizing videos...")
        self.preview_button.setEnabled(False)
        self.optimize_button.setEnabled(False)
        self.progress_bar.setValue(0)

        for directory_path in self.directory_paths:
            optimize_thread = OptimizationThread(
                directory_path, self.output_format, self.file_prefix, self.replace_spaces)
            optimize_thread.optimize_complete.connect(
                self.on_optimize_complete)
            optimize_thread.optimize_progress.connect(
                self.on_optimize_progress)
            optimize_thread.start()

            self.optimize_threads.append(optimize_thread)

    def optimize_thread_exists(self):
        """Check if an optimization thread is already running."""
        running_threads = [
            thread for thread in self.optimize_threads if thread.isRunning()]
        return len(running_threads) > 0

    def on_optimize_complete(self, msg):
        """Handle completion of the optimization process."""
        self.status_label.setText("All videos optimized!")
        self.preview_button.setEnabled(True)
        self.progress_bar.setValue(100)

    def on_optimize_progress(self, value):
        """Handle progress updates from the optimization thread."""
        self.progress_bar.setValue(value)

    def start_preview(self):
        """Start the preview process in a new thread."""
        self.preview_thread = PreviewThread(self.directory_paths)
        self.preview_thread.start()

    def closeEvent(self, event):
        """Handle window close event."""
        if not self.preview_thread is None and self.preview_thread.isRunning():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Cancel Preview?")
            msg_box.setText(
                "Preview is in progress. Are you sure you want to cancel?")
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            response = msg_box.exec()
            if response == QMessageBox.Yes:
                self.preview_thread.cancel()
                event.accept()
            else:
                event.ignore()


class AdvancedSettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set up the layout
        self.setup_layout()

        # Set the window properties
        self.setWindowTitle('Advanced Settings')
        self.setFixedSize(400, 200)

    def setup_layout(self):
        # Set up the widgets
        self.bitrate_label = QLabel("Bitrate (kbps):")
        self.bitrate_edit = QLineEdit("8000")
        self.bitrate_edit.setFixedWidth(70)
        self.bitrate_edit.setFixedHeight(20)
        self.bitrate_edit.setAlignment(Qt.AlignCenter)

        self.framerate_label = QLabel("Frame rate (fps):")
        self.framerate_edit = QLineEdit("30")
        self.framerate_edit.setFixedWidth(70)
        self.framerate_edit.setFixedHeight(20)
        self.framerate_edit.setAlignment(Qt.AlignCenter)

        self.quality_label = QLabel("Quality (CRF):")
        self.quality_edit = QLineEdit("18")
        self.quality_edit.setFixedWidth(70)
        self.quality_edit.setFixedHeight(20)
        self.quality_edit.setAlignment(Qt.AlignCenter)

        self.form_layout = QFormLayout()
        self.form_layout.addRow(self.bitrate_label, self.bitrate_edit)
        self.form_layout.addRow(self.framerate_label, self.framerate_edit)
        self.form_layout.addRow(self.quality_label, self.quality_edit)

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        # Set up the layouts
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.cancel_button)

        # Set up the main layout
        layout = QVBoxLayout()
        layout.addLayout(self.form_layout)
        layout.addStretch()
        layout.addLayout(button_layout)

        # Set the layout
        self.setLayout(layout)

    def get_settings(self):
        bitrate = self.bitrate_edit.text()
        framerate = self.framerate_edit.text()
        quality = self.quality_edit.text()
        return bitrate, framerate, quality


class OptimizationThread(QThread):

    optimize_complete = pyqtSignal(str)
    optimize_progress = pyqtSignal(int)

    def __init__(self, directory_path, output_format, file_prefix, replace_spaces):
        super().__init__()
        self.directory_path = directory_path
        self.output_format = output_format
        self.file_prefix = file_prefix
        self.replace_spaces = replace_spaces
        self.cancelled = False

    def run(self):
        """Optimize the videos in the selected directory."""
        try:
            if not self.directory_path:
                raise Exception("Please select a directory first.")

            self.optimize_progress.emit(0)

            # Get the list of video files in the directory
            video_files = [f for f in os.listdir(self.directory_path) if f.endswith(
                (".mp4", ".mov", ".avi", ".wmv", ".flv", ".mkv"))]
            total_files = len(video_files)

            if total_files == 0:
                raise Exception("No video files found in selected directory.")

            # Get the advanced settings
            settings_dialog = AdvancedSettingsDialog()
            if settings_dialog.exec_() == QDialog.Accepted:
                bitrate, framerate, quality = settings_dialog.get_settings()

            # Loop over the video files and optimize them
            progress_step = 100 / total_files
            for i, filename in enumerate(video_files):
                if self.cancelled:
                    raise Exception("Optimization cancelled.")

                old_path = os.path.join(self.directory_path, filename)

                # Rename the file
                new_filename = f"{self.file_prefix}{i+1}{self.output_format}"
                if self.replace_spaces:
                    new_filename = new_filename.replace(' ', '_')
                new_path = os.path.join(self.directory_path, new_filename)

                try:
                    os.rename(old_path, new_path)
                except OSError as e:
                    raise Exception(f"Error renaming {filename}: {e}")

                # Optimize the video
                cmd = f"ffmpeg -i \"{new_path}\" -c:v libx264 -preset slower -crf {
                    quality} -b:v {bitrate}k -c:a copy -r {framerate} \"{old_path}\""
                try:
                    subprocess.check_call(cmd, shell=True)
                    os.remove(new_path)
                except subprocess.CalledProcessError as e:
                    raise Exception(f"Error optimizing {filename}: {e}")

                # Update the progress bar
                self.optimize_progress.emit(int(round((i+1) * progress_step)))

            self.optimize_complete.emit("Optimization complete!")
        except Exception as e:
            traceback.print_exc()
            self.optimize_complete.emit(str(e))

    def cancel(self):
        """Cancel the optimization process."""
        self.cancelled = True


class PreviewThread(QThread):

    def __init__(self, directory_paths):
        super().__init__()
        self.directory_paths = directory_paths
        self.cancelled = False

    def run(self):
        """Preview the optimized videos in the selected directory."""
        try:
            if not self.directory_paths:
                raise Exception("Please select a directory first.")

            for directory_path in self.directory_paths:
                video_files = [f for f in os.listdir(directory_path) if f.endswith(
                    (".mp4", ".mov", ".avi", ".wmv", ".flv", ".mkv"))]
                total_files = len(video_files)

                if total_files == 0:
                    raise Exception(
                        "No video files found in selected directory.")

                progress_step = 100 / total_files
                for i, filename in enumerate(video_files):
                    if self.cancelled:
                        raise Exception("Preview cancelled.")

                    path = os.path.join(directory_path, filename)

                    # Preview the video
                    try:
                        subprocess.check_call(['xdg-open', path])  # Linux
                    except FileNotFoundError:
                        try:
                            subprocess.check_call(['open', path])  # macOS
                        except FileNotFoundError:
                            subprocess.check_call(
                                ['explorer', path])  # Windows

                    # Update the progress bar
                    progress = int(round((i+1) * progress_step))
                    self.emit_progress_update(
                        f"Previewing {filename} ({progress}% complete)...", progress)

            self.emit_progress_complete(f"All videos previewed successfully!")

        except Exception as e:
            traceback.print_exc()
            self.emit_progress_complete(str(e))

    def cancel(self):
        """Cancel the preview process."""
        self.cancelled = True

    def emit_progress_update(self, msg, progress):
        """Emit a progress update signal."""
        progress_str = f" ({progress}% complete)" if progress else ""
        self.progress_updated.emit(f"{msg}{progress_str}")

    def emit_progress_complete(self, msg):
        """Emit a progress complete signal."""
        self.progress_updated.emit(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor(142, 45, 197).lighter())
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    window = VideoOptimizationApp()
    sys.exit(app.exec_())
