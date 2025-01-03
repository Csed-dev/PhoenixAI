"""This module builds and runs a simple GUI application."""
from phoenixai.pipeline_transformation.gui import build_gui

if __name__ == '__main__':
    root = build_gui()
    root.mainloop()
