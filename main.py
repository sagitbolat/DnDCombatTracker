import tkinter as tk

class DraggableToken:
    def __init__(self, canvas, x, y, size, text, grid_size, cell_size, app):
        self.canvas = canvas
        self.size = size
        self.text = text
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.token = canvas.create_oval(x, y, x + 2 * size, y + 2 * size, fill="white", outline="black", tags="token")
        self.text_id = canvas.create_text(x + size, y + size, text=text, tags="token")
        self.dragging = False
        self.canvas.tag_bind(self.token, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.token, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.token, "<ButtonRelease-1>", self.stop_drag)
        self.canvas.tag_bind(self.text_id, "<ButtonPress-1>", self.start_drag)
        self.canvas.tag_bind(self.text_id, "<B1-Motion>", self.drag)
        self.canvas.tag_bind(self.text_id, "<ButtonRelease-1>", self.stop_drag)
        self.app = app
        self.canvas.tag_bind(self.token, "<ButtonPress-3>", self.delete_token)  # Right-click to delete
        self.canvas.tag_bind(self.text_id, "<ButtonPress-3>", self.delete_token)


    def start_drag(self, event):
        self.dragging = True
        self.canvas.tag_raise(self.token)
        self.canvas.tag_raise(self.text_id)

    def drag(self, event):
        if self.dragging:
            x, y = event.x, event.y
            self.canvas.coords(self.token, x - self.size, y - self.size, x + self.size, y + self.size)
            self.canvas.coords(self.text_id, x, y)

    def stop_drag(self, event):
        if self.dragging:
            self.dragging = False
            x, y = event.x, event.y
            grid_x = round((x - self.size) / self.cell_size) * self.cell_size + self.size
            grid_y = round((y - self.size) / self.cell_size) * self.cell_size + self.size
            self.canvas.coords(self.token, grid_x - self.size, grid_y - self.size, grid_x + self.size, grid_y + self.size)
            self.canvas.coords(self.text_id, grid_x, grid_y)

    def delete_token(self, event):
        self.canvas.delete(self.token)
        self.canvas.delete(self.text_id)
        self.app.tokens.remove(self)


class GridApp:
    def __init__(self, root, grid_size=8, screen_width = 1280, screen_height=720):
        self.root = root
        self.grid_size = grid_size
        self.cell_size = screen_height/grid_size
        self.token_size = self.cell_size/2

        self.frame = tk.Frame(root)
        self.frame.pack(side=tk.LEFT)

        self.canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg="grey")
        self.canvas.pack(side=tk.LEFT)

        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.token_name_entry = tk.Entry(self.control_frame)
        self.token_name_entry.pack()

        self.add_token_button = tk.Button(self.control_frame, text="Add Token", command=self.add_token_from_entry)
        self.add_token_button.pack()



        self.draw_grid()
        self.tokens = []

    def draw_grid(self):
        for i in range(self.grid_size):
            for j in range(self.grid_size):
                x, y = i * self.cell_size, j * self.cell_size
                self.canvas.create_rectangle(x, y, x + self.cell_size, y + self.cell_size, outline="white")

    def add_token(self, x, y, color="token"):
        grid_x = x * self.cell_size 
        grid_y = y * self.cell_size 
        token = DraggableToken(self.canvas, grid_x, grid_y, self.token_size, color, self.grid_size, self.cell_size, self)
        self.tokens.append(token)

    def add_token_from_entry(self):
        text = self.token_name_entry.get()
        if text:
            self.add_token(0, 0, text)
            self.token_name_entry.delete(0, tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = GridApp(root, 20, 720, 720)
    app.add_token(1, 1, "A")  # Tokens are now specified by grid coordinates
    app.add_token(3, 3, "B")
    root.mainloop()
