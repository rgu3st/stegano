from ast import Try
import tkinter as tk
import os
from tkinter.tix import WINDOW
from tkinter import filedialog
from PIL import ImageTk, Image
import numpy as np

'''
TODO: 
Add an "encrypt" checkbox 
    If there is a key pair in %APPDATA%, use that public key to encrypt. 
    Else: 
        Ask for a password (to encrypt the private key at rest)
        Generate a public/private key pair

How to load someone else's public key?
    When a user wants to send messages to new recipients: 
    Sender a request for the recipients public key, name, etc.,
        (Should this have an encrypted signature from us, to verify once it's returned?)
    Add the recipient to some sort of user file/database,
    From then on, you can send messages to them. 
'''

WINDOW_BG_COLOR = "#333"
FRAME_BG_COLOR = "#222"
IMAGE_FILENAME = ""
BYTE_LEN = 8
TERMINATOR = "#"
image1 = None
image1_PIL = None
messageBox = None
bytesToEncode = None
test_message = "Hello Hidden World!\n"  # For the test, I'll stop at a new line character.

APPFOLDER = ""

try:
    APPFOLDER = os.getenv('APPDATA')
    APPFOLDER += '/Stegano/'
    print(APPFOLDER)
    os.mkdir(APPFOLDER)
except FileExistsError:
    pass  # This is fine, we'll just use it
except FileNotFoundError:
    print('A parent path to %APPDATA% is somehow missing??')

filename = APPFOLDER + "tmp1.png"

window = tk.Tk()
window.title("Stegano - By Rob Guest")


frame_bg = tk.Frame(
    master=window,
    bg=WINDOW_BG_COLOR,
    width="1100",
    height="400",
)

frame_bg.pack(
    fill = tk.BOTH,
    side=tk.TOP,
    expand = True
    )

frame = tk.Frame(
    master = frame_bg,
    width="1100",
    bg=FRAME_BG_COLOR
    )


greeting = tk.Label(
    master = frame_bg,
    text="  Welcome To Stegano!  ", 
    font=("", 12),
    foreground="#ddd",
    background="#333",
    )
greeting.pack(pady=20)

frame.pack(
    side = tk.BOTTOM,
    fill=tk.BOTH,
    pady=20,
    padx = 20
    )


messageBox = tk.Text(
    bg="#1d1e1f",
    foreground="#ccc",
    master = frame, 
    width="60")

messageBox.grid(
    row = 0,
    column = 0,
    padx=20,
    pady=20)
messageBox.insert(1.0, "Type your text here! \nI'm making '#' the terminator now...\nThis is wonky, I should just add my own terminator manually...")
messageBox.insert(1.5, "some of ")


chkValue_encrypt = tk.BooleanVar() 
chkValue_encrypt.set(False)

def encrypt_checkbox_handle():
    if chkValue_encrypt.get() == True:
        try:
            print("Checking for cipher stuffs to use.")
            private_key = open(APPFOLDER + "\\cipher\\private.pem", "rt")
            public_key = open(APPFOLDER + "\\cipher\\public.pem", "rt")
            print("Private: \n" + private_key.read())
            print("Public: \n"+public_key.read())
        except FileNotFoundError:
            print('No cipher keys to use. TODO: generate some!')



encrypt_checkbox = tk.Checkbutton(
    master = frame,
    text="Encrypt message",
    command= encrypt_checkbox_handle,
    foreground="#111",
    background="#999",
    var = chkValue_encrypt
)

encrypt_checkbox.grid(
    row=1,
    column=0,
    padx=20,
    pady=20
)

image1_PIL = Image.open(filename)
image1 = ImageTk.PhotoImage(image1_PIL)

label_image = tk.Label(
    image = image1,
    master = frame,
    width = "640",
    height = "480",
    padx=20,
    pady=20
)

label_image.grid(
    row = 0, 
    column = 2,
    padx="20"
)

frame_buttons = tk.Frame(
    master = frame,
    bg=FRAME_BG_COLOR
)
frame_buttons.grid(
    row = 0,
    column = 1,
    pady=10
)

button_select_image = tk.Button(
    text = "Select Image",
    master=frame_buttons
)
button_select_image.grid(
    row=0,
    column=0,
    pady=10,
    padx=10
)

button_hide = tk.Button(
    text = "Hide Message!",
    master = frame_buttons
)
button_hide.grid(
    row=1,
    column=0,
    pady=10,
    padx=10
)

button_decode_hidden = tk.Button(
    text = "Decode Message", 
    master=frame_buttons
)

button_decode_hidden.grid(
    row=2,
    column=0,
    pady=10,
    padx=10
)


def update_message():
    global test_message
    test_message = messageBox.get('1.0', tk.END)
    test_message += TERMINATOR   # Not here?
    print(f"{ test_message }", end="")


def browseFiles(event):
    global filename
    global label_image
    global image1
    global image1_PIL
    filename = filedialog.askopenfilename(initialdir = APPFOLDER,
                                        title = "Select a File",
                                        filetypes = (("Image files",
                                                        "*.png*"),
                                                    ("all files",
                                                        "*.*")))
    print(f"Selected file was: {filename}")
    image1_PIL = Image.open(filename)
    image1 = ImageTk.PhotoImage(image1_PIL)
    label_image.configure(image=image1)
    label_image.img = image1


def hide_message(event):
    global filename
    global label_image
    global image1
    global image1_PIL
    global bitstream
    global test_message
    '''
    # Useful bits from https://www.pythoninformer.com/python-libraries/numpy/numpy-and-images/
    import numpy as np
    from PIL import Image
    img = Image.open('testgrey.png')
    array = np.array(img)
    array = 255 - array
    invimg = Image.fromarray(array)
    invimg.save('testgrey-inverted.png')'''

    # Grab the most recent version of the text to hide:
    update_message()

    # Do the Image stuffs:
    image1_PIL = Image.open(filename)
    img_array = np.array(image1_PIL)
    img_array = img_array
    test_message += TERMINATOR
    message_bytes =  test_message.encode('utf-8')  # I'm going to look for "LF", x0A, to end for now
    cur_message_byte = 0  # I have to manually track this. I think...
    cur_message_bit = 0
    count = 0
    char_count = 0
    for row in img_array:
        if char_count == len(message_bytes):
            print("Done encoding.")
            break
        for pixel in row:
            val = 0
            if char_count >= len(message_bytes)-1:
                break
            while val < 3:
                bit_value = (message_bytes[cur_message_byte]>>cur_message_bit) % 2
                if char_count < len(message_bytes):
                    print(f"{bit_value}", end='')
                if pixel[val] % 2 == 0 and bit_value != 0:  # If the LSB is 0 But the bit to set is a 1
                    pixel[val] |= 1  # Then set as 1, otherwise leave as a zero
                elif pixel[val] % 2 != 0 and bit_value == 0:  #LSB is 1 but needs to be zero:
                    pixel[val] = pixel[val] - 1  # -1 from an odd number makes LSB 0
                cur_message_bit = ( cur_message_bit + 1 ) % 8
                if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                    char_count += 1
                    print("  |||  Encoded: " + chr(message_bytes[cur_message_byte]))
                    cur_message_byte += 1
                val += 1
                count += 1
            

    print(f"Done encoding, saving to: {filename}")
    hidden_image_PIL = Image.fromarray(img_array)
    hidden_image_PIL.save(APPFOLDER + 'tmp1.png')
    hidden_image = ImageTk.PhotoImage(hidden_image_PIL)
    
    print("Saved.")

    label_image.configure(image=hidden_image)
    label_image.img = hidden_image

def decode_hidden_message(event):
    print("Decoding")
    # OK... I need to go through all the image pixels until I get to "LF", 0xA
    global filename
    global label_image
    global image1
    global image1_PIL
    global bitstream
    global test_message
    global BYTE_LEN
    image1_PIL = Image.open(filename)
    img_array = np.array(image1_PIL)
    img_array = img_array
    num_bytes_to_print = 8
    max_message_len = 200
    message_bytes =  [0]
    cur_message_byte = 0  # I have to manually track this. I think...
    cur_message_bit = 0
    count = 0
    for row in img_array:
        if chr(message_bytes[cur_message_byte]) == TERMINATOR:
            print(" |||  Terminator found. Exiting row. ")
            break
        if len(message_bytes) >= max_message_len:
            print("Max decode message length met. Stopping.")
            break
        for pixel in row:
            val = 0
            if len(message_bytes) >= max_message_len:
                break
            # Grab the current byte, shift it to make the current bit in the 1s spot and mod
            if chr(message_bytes[cur_message_byte]) == TERMINATOR:
                print(" |||  Terminator found. Exiting pixel. ")
                break
            while val < 3:
                if pixel[val] % 2 == 1:  # If the read value is 1, OR to set the message bit to 1
                    message_bytes[cur_message_byte] |= 1 << cur_message_bit
                    print("1", end="")
                else:  # Otherwise, leave this bit as 0
                    print("0", end="")
                cur_message_bit = ( cur_message_bit + 1 ) % BYTE_LEN
                if cur_message_bit == 0:  # If we roll back over from 8, increment the byte 
                    char = chr(message_bytes[cur_message_byte])
                    print("  |||  Decoded: " + char )
                    if char == TERMINATOR:
                        break
                    cur_message_byte += 1
                    message_bytes.append(0)
                val += 1
    message_ascii = ''.join(map(chr, message_bytes[0:-2]))
    print(f"Decoded message: {message_ascii}")
            
    

    
def clear_messageBox(event):
    global messageBox
    messageBox.delete(0.0, tk.END)

# Create an event handler
def handle_keypress(event):
    pass


# Bind keypress event to handle_keypress()
window.bind("<Key>", handle_keypress)

button_select_image.bind("<Button-1>", browseFiles)

button_hide.bind("<Button-1>", hide_message)

button_decode_hidden.bind("<Button-1>", decode_hidden_message)


messageBox.bind("<FocusIn>", clear_messageBox)
#messageBox.bind("<Leave>", update_message)
#messageBox.bind("<Any-KeyPress>", update_message)
label_image.img = image1

window.mainloop()
