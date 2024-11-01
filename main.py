import socket
import struct
import customtkinter as ctk
import threading

# Define the port number as a constant
PORT = 6454

# Set the customtkinter theme to dark
ctk.set_appearance_mode("dark")

class DMXEmulator:
    def __init__(self, master):
        self.master = master
        self.master.title("DMX Light Emulator")
        self.canvas = ctk.CTkCanvas(master, width=400, height=400, bg='#2e2e2e', highlightthickness=0)  # Dark grey color
        self.canvas.pack(fill=ctk.BOTH, expand=True)
        self.light = self.canvas.create_oval(150, 150, 250, 250, fill='black')
        
        # Add a Text widget to display DMX data
        self.dmx_text = ctk.CTkTextbox(master, height=20)
        self.dmx_text.pack(fill=ctk.BOTH, expand=True)

        # Bind the resize event to update the oval's position
        self.master.bind('<Configure>', self.resize)

    def update_light(self, r, g, b, data):
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.itemconfig(self.light, fill=color)
        
        # Clear the Text widget and insert the received DMX data
        self.dmx_text.delete(1.0, ctk.END)
        self.dmx_text.insert(ctk.END, f"DMX Data: {data}")

    def resize(self, event):
        # Center the oval on the canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.light, width//2 - 50, height//2 - 50, width//2 + 50, height//2 + 50)

def receive_dmx_command(emulator, sock):
    while True:
        try:
            data, _ = sock.recvfrom(65535)
            if len(data) >= 21:  # Ensure the packet is long enough to contain DMX data
                r, g, b = struct.unpack('BBB', data[18:21])
                emulator.master.after(0, emulator.update_light, r, g, b, data)
        except BlockingIOError:
            continue

if __name__ == "__main__":
    root = ctk.CTk()
    emulator = DMXEmulator(root)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))  # Bind to all interfaces on port 6454 (default for Art-Net)
    sock.setblocking(False)

    # Start the process of receiving DMX commands
    dmx_thread = threading.Thread(target=receive_dmx_command, args=(emulator, sock), daemon=True)
    dmx_thread.start()

    root.mainloop()
