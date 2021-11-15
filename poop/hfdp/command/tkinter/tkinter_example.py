import tkinter as tk


def main() -> None:
    root = tk.Tk()
    frame = tk.Frame(root)

    # lâmpada
    light = tk.Label(frame, text="light", bg="gray", height=1, width=5)

    # ações (commands)

    def set_light_yellow() -> None:
        light.config(bg="yellow")

    def set_light_gray() -> None:
        light.config(bg="gray")

    # botões

    # O padrão é usado para desacoplar quem executa o comando (botões)
    # de objetos que sabem realizar as solicitações (luz).
    # Nossos comandos são chamados de ações
    # e usam funções ao invés de uma classe.
    on_button = tk.Button(
        frame, text="On", command=set_light_yellow, height=1, width=5
    )
    off_button = tk.Button(
        frame, text="Off", command=set_light_gray, height=1, width=5
    )

    # desenha na tela
    on_button.pack()
    light.pack()
    off_button.pack()
    frame.pack()

    root.mainloop()
