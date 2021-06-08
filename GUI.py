import tkinter as tk
from tkinter import ttk
from gesture import Gesture
from PIL import Image, ImageTk

url = 'https://www.youtube.com/watch?v=wrf5KzT0954&t=195s'
wdWid = 400
wdHei = 400
color1 = '#EEFFBB'
color2 = '#CCFF99'


def callGesture():
    if checkVal.get():
        window.wm_attributes('-topmost', 1)
    else:
        window.wm_attributes('-topmost', 0)

    url = urlTxt.get()
    newGesture = Gesture(False, url)


window = tk.Tk()
window.title('Movie Controller')
window.geometry('400x350')
window['background'] = color1

checkVal = tk.BooleanVar()
checkVal.set(False)
checkBtn = tk.Checkbutton(
    window, text='Pin this page', bg=color1, var=checkVal)
checkBtn.pack(side='top')

urlTxt = tk.Entry(window, width=50, text=url)
urlTxt.insert(0, url)
urlTxt.pack(side='top')

gesInc = ttk.Treeview(window, heigh=11, column=['a1', 'a2'], show='headings')
gesInc.heading('a1', text='Function')
gesInc.heading('a2', text='Gesture')
gesInc.column('a1', width=70, anchor='center')
gesInc.column('a2', width=150, anchor='center')
gesInc.insert('', 0, values=['播放/暫停', '左手食指'])
gesInc.insert('', 1, values=['全螢幕', '左手比5'])
gesInc.insert('', 2, values=['上一部', '左手大拇指'])
gesInc.insert('', 3, values=['禁音', '左手小拇指'])
gesInc.insert('', 4, values=['倒轉5秒', '左手食指中指距離短'])
gesInc.insert('', 5, values=['快進5秒', '左手食指中指距離長'])
gesInc.insert('', 6, values=['下一部', '右手大拇指'])
gesInc.insert('', 7, values=['劇院模式', '右手比5'])
gesInc.insert('', 8, values=['字幕', '右手小拇指'])
gesInc.insert('', 9, values=['大聲', '右手食指中指距離短'])
gesInc.insert('', 10, values=['小聲', '右手食指中指距離長'])
gesInc.pack(side='top')

button = tk.Button(window, text='Start', bg=color2, command=callGesture)
button.pack(side='bottom', fill='x')

window.mainloop()

# imageTk=ImageTk.PhotoImage(file='stars.jpg')
# canvas=tk.Canvas(window,width=wdWid,heigh=wdHei,bg='red')
#canvas.create_image(0,0, anchor='nw', image=imageTk)
# canvas.pack()

# backgroundLabel=tk.Label(image=imageTk)
# backgroundLabel.place(x=0,y=0)
# backgroundLabel.pack()
