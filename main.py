import socket
import struct
import customtkinter as ctk
import threading

# Define the port number as a constant
PORT = 6454

# Set the customtkinter theme to dark
ctk.set_appearance_mode("dark")

class DMXEmulator:
    def __init__(self, master, start_index=18):
        self.master = master
        self.master.title("DMX Light Visualizer")
        self.start_index = start_index  # Store the starting index for slicing
        
        # Create a canvas to display the light
        self.canvas = ctk.CTkCanvas(master, width=400, height=400, bg='#2e2e2e', highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True)
        
        # Create an oval to represent the light
        self.light = self.canvas.create_oval(150, 150, 250, 250, fill='black')
        
        # Add a Text widget to display DMX data
        self.dmx_text = ctk.CTkTextbox(master, height=20)
        self.dmx_text.pack(fill=ctk.BOTH, expand=True)

        # Add an entry widget to input the start index
        self.start_index_entry = ctk.CTkEntry(master, placeholder_text="Enter start index")
        self.start_index_entry.insert(0, str(self.start_index - 17))  # Display adjusted start index
        self.start_index_entry.pack(pady=5)  # Add padding to prevent scaling

        # Add a button to update the start index
        self.update_button = ctk.CTkButton(master, text="Update Start Index", command=self.update_start_index)
        self.update_button.pack(pady=5)  # Add padding to prevent scaling

        # Bind the resize event to update the oval's position
        self.master.bind('<Configure>', self.resize)

    def update_light(self, r, g, b, data):
        # Update the color of the light
        color = f'#{r:02x}{g:02x}{b:02x}'
        self.canvas.itemconfig(self.light, fill=color)
        
        # Clear the Text widget and insert the received DMX data in decimal format, skipping the first 17 bytes
        self.dmx_text.delete(1.0, ctk.END)
        dmx_data_decimal = [str(byte) for byte in data[18:]]
        self.dmx_text.insert(ctk.END, f"DMX Data: {', '.join(dmx_data_decimal)}")

    def resize(self, event):
        # Center the oval on the canvas
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        self.canvas.coords(self.light, width//2 - 50, height//2 - 50, width//2 + 50, height//2 + 50)

    def update_start_index(self):
        # Update the start index based on user input
        try:
            new_start_index = int(self.start_index_entry.get()) + 17  # Adjust the start index
            self.start_index = new_start_index
            print(f"Start index updated to: {self.start_index}")
        except ValueError:
            print("Invalid input. Please enter a valid integer.")

def receive_dmx_command(emulator, sock):
    while True:
        try:
            data, _ = sock.recvfrom(1024)  # Reduce buffer size to 1024 bytes
            if len(data) >= emulator.start_index + 3:  # Ensure the packet is long enough to contain DMX data
                r, g, b = struct.unpack('BBB', data[emulator.start_index:emulator.start_index + 3])
                emulator.master.after(0, emulator.update_light, r, g, b, data)
        except BlockingIOError:
            continue

if __name__ == "__main__":
    root = ctk.CTk()
    emulator = DMXEmulator(root, start_index=18)  # You can change the start_index here if needed

    # Create and configure the socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('0.0.0.0', PORT))  # Bind to all interfaces on the specified port
    sock.setblocking(False)

    # Start the process of receiving DMX commands in a separate thread
    dmx_thread = threading.Thread(target=receive_dmx_command, args=(emulator, sock), daemon=True)
    dmx_thread.start()

    # Start the Tkinter main loop
    root.mainloop()
