import tkinter as tk


def main() -> None:
    root = tk.Tk()
    frame = tk.Frame(root)

    # light
    light = tk.Label(frame, text="light", bg="gray", height=1, width=5)

    # actions

    def set_light_yellow() -> None:
        light.config(bg="yellow")

    def set_light_gray() -> None:
        light.config(bg="gray")

    # buttons
    on_button = tk.Button(
        frame, text="On", command=set_light_yellow, height=1, width=5
    )
    off_button = tk.Button(
        frame, text="Off", command=set_light_gray, height=1, width=5
    )

    # draw
    on_button.pack()
    light.pack()
    off_button.pack()
    frame.pack()

    root.mainloop()
