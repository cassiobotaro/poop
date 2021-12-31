import tkinter as tk


def main() -> None:
    root = tk.Tk()
    frame = tk.Frame(root)

    int_var = tk.IntVar()

    def incr() -> None:
        int_var.set(int_var.get() + 1)

    button = tk.Button(frame, text="+1", command=incr, height=1, width=5)
    label = tk.Label(frame, textvariable=int_var)

    # desenha na tela
    button.pack()
    label.pack()
    frame.pack()

    root.mainloop()
