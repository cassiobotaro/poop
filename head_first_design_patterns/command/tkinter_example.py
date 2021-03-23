"""
Notes:
    - create an application with two buttons and a
    label to represent a light
    - command pattern is used to decouple who executes the command (buttons)
    from objects that know how to perform the requests (light)
    - our commands are called actions and use function instead of a class
"""
import tkinter as tk


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # light
        self.light = tk.Label(self, text="light", bg="gray", height=1, width=5)

        # actions
        def set_light_yellow():
            self.light.config(bg="yellow")

        def set_light_gray():
            self.light.config(bg="gray")

        # buttons
        self.on_button = tk.Button(
            self, text="On", command=set_light_yellow, height=1, width=5
        )
        self.off_button = tk.Button(
            self, text="Off", command=set_light_gray, height=1, width=5
        )

        # draw on screen
        self.on_button.pack()
        self.light.pack()
        self.off_button.pack()


root = tk.Tk()
app = Application(master=root)
app.mainloop()
