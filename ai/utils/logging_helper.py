# ai/utils/logging_helper.py
import sys

class Tee:
    def __init__(self, file_path):
        """
        Industrial Logger: Captures all stdout and mirrors it to a physical file.
        Ensures real-time write for live monitoring.
        """
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Usamos 'a' (append) para que si el proceso se reinicia, el historial de logs no se borre
        self.file = open(file_path, "a", encoding="utf-8")
        self.stdout = sys.stdout

    def write(self, data):
        if data:
            self.file.write(data)
            self.stdout.write(data)
            # FORCE REAL-TIME DISK WRITE
            self.file.flush() 
            self.stdout.flush()

    def flush(self):
        self.file.flush()
        self.stdout.flush()

    def close(self):
        self.file.close()