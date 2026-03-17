try:
    from psychopy import core, visual
except ImportError:
    print("Psychopy not downloaded.")

class MainExp:
    def __init__(self, block_list):
        self.blocks = block_list

        height, width = 1280, 720
        self.win = visual.Window(size=[height, width], fullscr=False, color="black", units="norm")