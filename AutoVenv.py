from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import os
from tkinter.scrolledtext import ScrolledText
from subprocess import Popen, PIPE
from threading import Thread, Lock
import tkinter as tk
#WINDOW
w = Tk()
w.title('AutoVenv')
w.geometry("550x655")
w.resizable(False,False)

user =  os.getlogin()
desktop = f'C:/Users/{user}/Desktop'
venv_dir = ''

class Console(ScrolledText):
    """
    Simple console that can execute commands
    """

    def __init__(self, master, **kwargs):
        # The default options:
        text_options = {"state": "disabled",
                        "bg": "#ffffff",
                        "fg": "#08c614",
                        "font": "Roboto 14",
                        "width":"46",
                        "height":"6",
                        "wrap":"word",
                        "selectbackground": "orange"}
        # Take in to account the caller's specified options:
        text_options.update(kwargs)
        super().__init__(master, **text_options)

        self.proc = None # The process
        self.text_to_show = "" # The new text that we need to display on the screen
        self.text_to_show_lock = Lock() # A lock to make sure that it's thread safe

        
        self.show_text_loop()

    def clear(self) -> None:
        """
        Clears the Text widget
        """
        super().config(state="normal")
        super().delete("0.0", "end")
        super().config(state="disabled")

    def show_notification(self,func=None)-> None:
        """Calls the func on run completion
        """
        btn6.config(state='normal',text='Open venv folder',font='Roboto 16',width=20,bg='#458BC6',fg='white',command=lambda:os.system('start  explorer "'+str(entry2.get().replace("/","\\")+'"')))
        # btn8 = Button(frame2,text='Activate venv',cursor='hand2',font='Roboto 14',width=15,bg='#458BC6',fg='white')
        # btn8.grid(row=3,column=0,sticky='e',padx=10)
        btn9 = Button(frame2,text='New venv',cursor='hand2',font='Roboto 16',width=20,bg='#458BC6',fg='white',command=lambda:btn6.config(width=42,text='Create',command=update_cmd) or entry3.delete(0,END) or textbox1.delete(1.0,END) or current_entry.delete(1.0,END) or  console.clear() or btn9.destroy())
        btn9.grid(row=3,column=0,sticky='e',padx=20)

    def show_text_loop(self) -> None:
        """
        Inserts the new text into the `ScrolledText` wiget
        """
        new_text = ""
        # Get the new text that needs to be displayed
        with self.text_to_show_lock:
            new_text = self.text_to_show.replace("\r", "")
            self.text_to_show = ""

        if len(new_text) > 0:
            # Display the new text:
            super().config(state="normal")
            super().insert("end", new_text)
            super().see("end")
            super().config(state="disabled")

        # After 100ms call `show_text_loop` again
        super().after(100, self.show_text_loop)

    def run(self, command:str) -> None:
        """
        Runs the command specified
        """
        self.stop()
        thread = Thread(target=self._run, daemon=True, args=(command, ))
        thread.start()

    def _run(self, command:str) -> None:
        """
        Runs the command using subprocess and appends the output
        to `self.text_to_show`
        """
        super().config(state="normal")
        super().insert("end", 'Creating Venv...')
        super().see("end")
        super().config(state="disabled")
        
        self.proc = Popen(command, shell=True, stdout=PIPE)

        try:
            while self.proc.poll() is None:
                text = self.proc.stdout.read(1).decode()
                with self.text_to_show_lock:
                    self.text_to_show += text

            self.proc = None
            self.show_notification()
        except AttributeError:
            # The process ended prematurely
            pass

    def stop(self, event:tk.Event=None) -> None:
        """
        Stops the process.
        """
        try:
            self.proc.kill()
            self.proc = None
        except AttributeError:
            # No process was running
            pass

    def destroy(self) -> None:
        # Stop the process if the text widget is to be destroyed:
        self.stop()
        super().destroy()

def run_command_in_entry(cmd):
        console.clear()
        console.run(cmd)   
        # console.run('cls')   

def get_dir():
    venv_dir = filedialog.askdirectory(parent=w,initialdir=os.getcwd(),
                                 title="Select Directory for Venv")
    entry2.delete(0,END)
    entry2.insert(0, venv_dir)
    update_cmd(create=False)

def get_file():
    my_filetypes = [('Text File', '*.txt'),('All files', '.*')]
    req_loc = filedialog.askopenfilename(parent=w,
                                initialdir=os.getcwd(),
                                title="Please select Requirements.txt file:",
                                filetypes=my_filetypes)
    entry3.delete(0,END)
    entry3.insert(0, req_loc)
    update_cmd(create=False)



def update_cmd(create='true'):
    venv_name = entry1.get()
    venv_loc = entry2.get()
    req_file = entry3.get()
    packedges = ''.join([i for i in textbox1.get(1.0, "end-1c")]).replace('\n',' ')

    activate = r'\Scripts\activate.bat'
    run_env = f'start cmd /k  {venv_name}/{activate} && cls'

    if (req_file and packedges):
        cmd = f'cd "{venv_loc}" && python -m venv {venv_name} && {venv_name}{activate} && pip install -r "{req_file}" && pip install {packedges} &&   cd "{venv_loc}" &&  {run_env}'
    elif req_file:
        cmd = f'cd "{venv_loc}" && python -m venv {venv_name} && {venv_name}{activate} && pip install -r "{req_file}" &&  cd "{venv_loc}" &&   {run_env}'
    elif packedges:
        cmd = f'cd "{venv_loc}" && python -m venv {venv_name} && {venv_name}{activate} && pip install {packedges} &&  cd "{venv_loc}" &&  {run_env}'
    else:
        cmd = f'cd "{venv_loc}" && python -m venv {venv_name} && {venv_name}{activate} &&  cd "{venv_loc}" &&   {run_env}'            
        

    current_entry.delete('1.0',END)
    current_entry.insert('1.0', cmd)


    if create == 'true':
        if not (packedges or req_file):
            choice = messagebox._show('Not Found Requirements.txt or Packedges','New venv will be created without any additional Packedges or requirements.txt file',"warning","yesno")
            if choice == 'yes':
                btn6.config(state='disabled',bg='#bdbcbb',text='Creating...')
                run_command_in_entry(f'{current_entry.get(1.0, "end-1c")}')
            else:
                pass
        elif not req_file:
            choice = messagebox._show('No Requirements.txt Found','New VENV will be created without requirements.txt',"warning","yesno")
            if choice == 'yes':
                btn6.config(state='disabled',bg='#bdbcbb',text='Creating...')
                run_command_in_entry(f'{current_entry.get(1.0, "end-1c")}')
            else:
                pass                

        elif not packedges:
            choice = messagebox._show('No Additional Packedges to Install','New venv will be created without any additional Packedges',"warning","yesno")
            if choice == 'yes':
                btn6.config(state='disabled',bg='#bdbcbb',text='Creating...')
                run_command_in_entry(f'{current_entry.get(1.0, "end-1c")}')
            else:
                pass
        else:
            btn6.config(state='disabled',bg='#bdbcbb',text='Creating...')
            run_command_in_entry(f'{current_entry.get(1.0, "end-1c")}')  




###################### UI ##############################
#FRAME1
frame = LabelFrame(w, text=" Venv ",font='Roboto 15')
frame.pack(fill=BOTH, padx=5, pady=5)

lb1 = Label(frame,text='Venv Name',font='Roboto 15')
lb1.grid(row=0,column=0,pady=17,sticky='nw',padx=10)
lb2 = Label(frame,text='Install Directory',font='Roboto 15')
lb2.grid(row=1,column=0,sticky='w',pady=10,padx=10)
lb3 = Label(frame,text='Requirements.txt',font='Roboto 15')
lb3.grid(row=2,column=0,pady=17,sticky='nw',padx=10)
lb4 = Label(frame,text='Install Packedges',font='Roboto 15')
lb4.grid(row=3,column=0,pady=17,sticky='nw',padx=10)

entry1 = Entry(frame,font='Roboto 15',width=25)
entry1.grid(row=0,column=1,padx=10)
entry1.insert(0,'env')
entry2 = Entry(frame,font='Roboto 15',width=25)
entry2.grid(row=1,column=1,padx=10)
entry2.insert(0, desktop)
entry3 = Entry(frame,font='Roboto 15',width=25)
entry3.grid(row=2,column=1,padx=0)

textbox1 = Text(frame,height=3,width=25,font='Roboto 15',wrap=WORD,bg='#ffffff')
textbox1.grid(row=3,column=1,pady=17)

btn1 = Button(frame,text='📝',cursor='hand2',font='Roboto 11',width=3,command=lambda:entry1.delete(0,END))
btn1.grid(row=0,column=2)
btn2 = Button(frame,text='📁',cursor='hand2',font='Roboto 11',width=3,command=get_dir)
btn2.grid(row=1,column=2)
btn3 = Button(frame,text='📁',cursor='hand2',font='Roboto 11',width=3,command=get_file)
btn3.grid(row=2,column=2)
btn4 = Button(frame,text='📝',cursor='hand2',font='Roboto 11',width=3,command=lambda:textbox1.delete('1.0',END))
btn4.grid(row=3,column=2,pady=17,sticky='ne')





#FRAME 2
frame2 = LabelFrame(w,text='')
frame2.pack(fill="both", expand="yes", padx=5, pady=5)

current_cmd = Label(frame2,text='@Current Command',cursor='hand2',font='Roboto 15')
current_cmd.grid(row=0,column=0,sticky='w',padx=10)
current_cmd.bind('<Button-1>',update_cmd)

current_entry = Text(frame2,font='Roboto 14',height=3,wrap=WORD,width=46)
current_entry.grid(row=1,column=0,pady=10,padx=10,sticky='w')

btn6 = Button(frame2,text='Create',width=42,cursor='hand2',font='Roboto 16',bg='#458BC6',fg='white',command=update_cmd)
btn6.grid(row=3,column=0,sticky='w',padx=10)

console = Console(frame2)
console.grid(row=2,column=0,sticky='w',padx=10,pady=10)

w.mainloop()
