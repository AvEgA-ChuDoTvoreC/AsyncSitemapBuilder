import sys
import time


class ProgressBar:
    def __init__(self):
        self.progress = float()
        self.percent = str()
        self.status = str()
        self.progress_bar = None
        self.text = str()
        self.barLength = int()
        self.block = None
        self.bar_element = None
        self.text = str()
        self.extra = '.'
        self.cnt = 0
        self.dots = ['.', '..', '...']

    def update_progress(self, progress, barLength=10, bar_element="█", text="Percent"):
        """update_progress() : Displays or updates a console progress bar
        # Accepts a float between 0 and 1. Any int will be converted to a float.
        # A value under 0 represents a 'halt'.
        # A value at 1 or bigger represents 100%"""

        self.progress = progress
        self.barLength = barLength  # Modify this to change the length of the progress bar
        self.bar_element = bar_element
        self.text = text

        try:
            if isinstance(self.progress, int):
                self.progress = float(self.progress)
            if not isinstance(self.progress, float):
                self.progress = 0
                self.status = "error: progress var must be float\r\n"
            if self.progress < 0:
                self.progress = 0
                self.status = "Halt...\r\n"
            if self.progress >= 1:
                self.progress = 1
                self.status = "Done...\r\n"

            self.percent = self.progress * 100
            self.block = int(round(self.barLength * self.progress))
            self.progress_bar = self.bar_element * self.block + " " * (barLength - self.block)

            self.cnt += 1
            if self.cnt >= len(self.dots):
                self.cnt = 0
            self.extra = self.dots[self.cnt]

            if self.status:
                self.text = f"\r {self.percent:.1f}% |{self.progress_bar}| {self.text} {self.status}"
            else:
                self.text = f"\r {self.percent:.1f}% |{self.progress_bar}| {self.text} {self.extra}"
            sys.stdout.write(self.text)
            sys.stdout.flush()

        except Exception as err:
            sys.stdout.write(str(err))
            self.status = "Fail...\r\n"
            self.text = f"\r {self.percent:.1f}% |{self.progress_bar}| {self.text} {self.status}"
            sys.stdout.write(self.text)
            sys.stdout.flush()
            sys.exit(1)


if __name__ == '__main__':
    pr_bar = ProgressBar()
    print("")
    print("progress : 0->1")
    for i in range(101):
        time.sleep(0.1)
        pr_bar.update_progress(i / 100.0)

    print("")
    print("Test completed")
    time.sleep(1)

    # update_progress test script
    # print("progress : 'hello'")
    # update_progress("hello")
    # time.sleep(1)
    #
    # print("progress : 3")
    # update_progress(30000)
    # time.sleep(1)
    #
    # print("progress : [23]")
    # update_progress([2300])
    # time.sleep(1)
    #
    # print("")
    # print("progress : -10")
    # update_progress(-10000)
    # time.sleep(2)
    #
    # print("")
    # print("progress : 10")
    # update_progress(100000)
    # time.sleep(2)

    r"""
    from tqdm import tqdm
    
    
    for i in tqdm(range(100000), total=100000):
        pass
    
    import time
    import sys
    
    toolbar_width = 10
    
    # setup toolbar
    sys.stdout.write("[{}]".format(" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1))  # return to start of line, after '['
    # sys.stdout.write("]")
    sys.stdout.flush()
    
    for i in range(toolbar_width):
        time.sleep(0.1) # do real work here
        # update the bar
        sys.stdout.write("█")
        sys.stdout.flush()
    
    sys.stdout.write("]\n") # this ends the progress bar
    """