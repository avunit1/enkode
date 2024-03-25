import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import io  # Add the import statement for the io module
from PIL import Image, ImageTk
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad

def aes_encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = cipher.iv
    return iv, ct_bytes

def aes_decrypt(iv, ct, key):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt

def derive_key(password):
    hasher = SHA256.new(password.encode())
    return hasher.digest()

def display_image_in_square(img_data):
    global img_label  # Define img_label as a global variable

    image = Image.open(io.BytesIO(img_data))
    width, height = image.size
    square_size = min(outline_square.winfo_width(), outline_square.winfo_height())

    # Calculate the scaling factor for resizing the image while maintaining aspect ratio
    aspect_ratio = width / height
    if aspect_ratio > 1:  # Landscape orientation
        scaling_factor = square_size / width
    else:  # Portrait orientation or square
        scaling_factor = square_size / height

    # Resize the image while maintaining aspect ratio
    new_width = int(width * scaling_factor)
    new_height = int(height * scaling_factor)
    resized_image = image.resize((new_width, new_height))

    # Clear any existing canvas
    for widget in outline_square.winfo_children():
        widget.destroy()

    # Create a new canvas inside the square
    canvas = tk.Canvas(outline_square, width=square_size, height=square_size, bg="black")
    canvas.pack()

    # Calculate position to center the image within the canvas
    x_offset = (square_size - new_width) // 2
    y_offset = (square_size - new_height) // 2

    # Convert PIL Image to Tkinter PhotoImage
    photo_image = ImageTk.PhotoImage(resized_image)

    # Display the image on the canvas
    canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=photo_image)
    canvas.image = photo_image  # Keep a reference to prevent garbage collection

def encode_image():
    global key_entry

    filename = filedialog.askopenfilename(title="Select Image File", filetypes=(("Image files", "*.png;*.jpg;*.jpeg;*.gif"), ("All files", "*.*")))
    if filename:
        with open(filename, "rb") as img_file:
            img_data = img_file.read()
            display_image_in_square(img_data)  # Display the image in the square
            key_entry = tk.Entry(root, show='*', width=20, bg="white", bd=5)
            key_entry.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

            encode_button.configure(command=lambda: encode_image_process(filename))

def encode_image_process(filename):
    global key_entry
    encryption_key = key_entry.get()
    if encryption_key:
        key = derive_key(encryption_key)
        with open(filename, "rb") as img_file:
            img_data = img_file.read()
            iv, encoded_data = aes_encrypt(img_data, key)
            text = iv + encoded_data
            text_filename = os.path.splitext(filename)[0] + ".txt"
            with open(text_filename, "wb") as text_file:
                text_file.write(text)
                messagebox.showinfo("Success", "Image encoded successfully!")
def decode_image():
    filename = filedialog.askopenfilename(title="Select Text File", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
    if filename:
        password = simpledialog.askstring("Input", "Enter Decryption Key:", show='*')
        if password:
            key = derive_key(password)
            with open(filename, "rb") as text_file:
                text = text_file.read()
                iv = text[:16]  # IV is 16 bytes
                encoded_data = text[16:]
                try:
                    decoded_data = aes_decrypt(iv, encoded_data, key)
                    img_filename = os.path.splitext(filename)[0] + "_decrypted.png"
                    with open(img_filename, "wb") as img_file:
                        img_file.write(decoded_data)
                        messagebox.showinfo("Success", "Image decrypted successfully!")
                except Exception as e:
                    messagebox.showerror("Decryption Error", str(e))

def center_buttons(event=None):
    window_width = root.winfo_width()
    window_height = root.winfo_height()
    x_position_column1 = window_width * 0.1  # 10% of window width
    y_position_open = window_height // 2 - 90 - 20
    y_position_encrypt = window_height // 2 + 60 + 20

    x_position_column2 = window_width * 0.6

    open_file_button.place(x=x_position_column1, y=y_position_open)
    open_button.place(x=x_position_column1, y=y_position_open + 60 + 10)
    decode_button.place(x=x_position_column2, y=y_position_encrypt)
    encode_button.place(x=x_position_column2, y=y_position_encrypt + 60 + 10)

def update_square(event=None):
    window_width = root.winfo_width()
    window_height = root.winfo_height()

    outline_square_side = int(window_height * 0.9)
    gap_from_top = int(window_height * 0.05)  # Gap from the top and bottom
    gap_from_side = gap_from_top  # Make it the same as the gap from top
    outline_square_x = window_width - outline_square_side - gap_from_side
    outline_square_y = gap_from_top

    outline_square.place(x=outline_square_x, y=gap_from_top, width=outline_square_side, height=outline_square_side)

# GUI setup
root = tk.Tk()
root.title("Enkode")
root.configure(bg="#121212")  # Background color

# Set window size to 40% of screen size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width = int(screen_width * 0.4)
window_height = int(screen_height * 0.4)
root.geometry(f"{window_width}x{window_height}")

# Set font color
root.option_add("*Font", "font.otf 10 bold")
root.option_add("*foreground", "#ffffff")

# Calculate button position
x_position = window_width * 0.1  # 10% of window width

open_button = tk.Button(root, text="Open Image", command=encode_image, fg="#ffffff", bg="#3700B3", width=10, height=2)
open_file_button = tk.Button(root, text="Open File", command=encode_image, fg="#ffffff", bg="#3700B3", width=10, height=2)
encode_button = tk.Button(root, text="Encrypt Image", command=encode_image, fg="#ffffff", bg="#3700B3", width=10, height=2)
decode_button = tk.Button(root, text="Decrypt Image", command=decode_image, fg="#ffffff", bg="#3700B3", width=10, height=2)

open_file_button.place(x=x_position, y=window_height // 2 - 90 - 20)
open_button.place(x=x_position, y=window_height // 2 + 20)
encode_button.place(x=x_position * 3.5, y=window_height // 2 - 90 - 20)
decode_button.place(x=x_position * 3.5, y=window_height // 2 + 20)

# Text above buttons
text_label = tk.Label(root, text="ENKODE", font=("font.otf", int(window_height * 0.0425)), fg="#ffffff", bg="#121212")
text_label.place(relx=0.1, rely=0.1, anchor=tk.W)

# Bind the function to resize event
root.bind("<Configure>", center_buttons)
root.bind("<Configure>", update_square)

# Create grey outline square
outline_square = tk.Frame(root, bg="#121212", highlightbackground="grey", highlightthickness=5)

# Initialize key entry widget
key_entry = tk.Entry(root, show='*', width=20, bg="white", bd=5)
key_entry.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

# Define img_label
img_label = tk.Label(root)

# Update square size and position
update_square()

root.mainloop()
