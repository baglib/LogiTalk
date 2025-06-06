from customtkinter import*
from socket import*
import threading 
from PIL import Image
import base64
import io     

class Registerwindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("300x300")
        self.title("Реєстрація")
        self.username = None
        self.label = CTkLabel(self,text="Вхід в LogiTalk",font = ("Arial",20,"bold"))
        self.label.pack(pady=40)
        self.name_entry = CTkEntry(self,placeholder_text="Введіть ім'я")
        self.name_entry.pack()
        self.host_entry = CTkEntry(self,placeholder_text="Введіть хост серверу")
        self.host_entry.pack()
        self.port_entry = CTkEntry(self,placeholder_text="Введіть порт серверу")
        self.port_entry.pack()

        self.btn_sumbit = CTkButton(self,text="Зареєструватися",command=self.start_chat)
        self.btn_sumbit.pack(pady=5)
    def start_chat(self):
        self.username = self.name_entry.get()
        try:
            self.sock = socket(AF_INET,SOCK_STREAM)
            self.sock.connect((self.host_entry.get(),int(self.port_entry.get)))
            hello = f"TEXT@{self.username}@[SYSTEM]{self.username}приєднався до чату!\n"
            self.sock.send(hello.encode())

            self.destroy()

            win = MainWindow(self.sock,self.username)
            win.mainloop()

        except:
           print("Не вділося підключитися до сервера")


class MainWindow(CTk):
    def __init__(self,sock,username):
        super().__init__()
        self.sock = sock
        self.username = username
        self.geometry("400x300")
        self.frame=CTkFrame(self,fg_color="light blue",width=200,height=self.winfo_height())
        self.frame.pack_propagate(False)
        self.frame.configure(width=0)

        self.frame.place(x=0,y=0)
        self.is_show_menu = False
        self.frame_width = 0

        self.label = CTkLabel(self.frame,text="Введіть налаштування")
        self.label.pack(pady=30)
        self.entry = CTkEntry(self.frame)
        self.entry.pack()
        self.btn_save = CTkButton(self.frame,text="Зберегти",command=self.save_name)
        self.btn_save.pack()

        self.btn = CTkButton(self,text="▶️",command=self.togle_show_menu,width=30)
        self.btn.place(x=0,y=0)

        self.chat_text = CTkTextbox(self,state="disabled")
        self.chat_text.place(x=0,y=30)

        self.message_input = CTkEntry(self,placeholder_text="Введіть повідомлення")
        self.message_input.place(x=0,y=250)

        self.btn_send = CTkButton(self,text="▶️",width=30,command=self.send_message)
        self.btn_send.place(x=200,y=250)


        self.adaptive_ui()

        self.label_theme = CTkOptionMenu(self.frame,values=["Темна","Світла"],command = self.change_theme)
        self.label_theme.pack(side="bottom",pady=20)
        self.theme = None
        self.username = "Sasha"
        



    
    def togle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()
    def show_menu(self):
        if self.frame_width <=200:
            self.frame_width +=5
            self.frame.configure(width=self.frame_width,height=self.winfo_height())
            if self.frame_width>=30:
                self.btn.configure(width=self.frame_width,text="◀️")
        if self.is_show_menu:
            self.after(10,self.show_menu)

    def close_menu(self):
        if self.frame_width >=0:
            self.frame_width -=5
            self.frame.configure(width=self.frame_width,height=self.winfo_height())
            if self.frame_width>=30:
                self.btn.configure(width=self.frame_width,text="▶️")
        if not self.is_show_menu:       
            self.after(10,self.close_menu)

    def adaptive_ui(self):
        self.chat_text.configure(width=self.winfo_width()-self.frame.winfo_width(),height=self.winfo_height()-self.message_input.winfo_height()-30)
        self.chat_text.place(x=self.frame.winfo_width())
        self.message_input.configure(width=self.winfo_width()-self.frame.winfo_width()-self.btn_send.winfo_width())
        self.message_input.place(x=self.frame.winfo_width(),y=self.winfo_height()-self.btn_send.winfo_height())
        self.btn_send.place(x=self.winfo_width()-self.btn_send.winfo_width(),y=self.winfo_height()-self.btn_send.winfo_height())
        self.after(20,self.adaptive_ui)
    def change_theme(self,value):
        if value == "Темна":
            set_appearance_mode("dark")
        else:
            set_appearance_mode("light")
    def add_message(self,text):
       self.chat_text.configure(state="normal")
       self.chat_text.insert(END, "Я:" + text + "\n")
       self.chat_text.configure(state="disable")
    def send_message(self):
        message = self.message_input.get()
        #self.username = self.entry.get()
        if message:
            self.add_message(f"{self.username}:{message}")
            data  =f"TEXT@{self.username}@{message}\n"
            try:
                self.sock.sendall(data.encode())
            except:
                pass
        self.message_input.delete(0,END)

    def recv_message(self):
        buffer = ""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                buffer += chunk.decode()

                while "\n" in buffer:
                    line, buffer = buffer.split("\n ,1")
                    self.handle_line(line.strip())
            except:
                break
        self.selfsock.close()
    def handle_line(self,line):
        if not line:
            return
        parts = line.split("@",3)
        msg_type = parts[0]

        if msg_type == "TEXT":
            if len(parts) >=3:
                author = parts[1]
                messsage = parts[2]
                self.add_message(f"{author}:{messsage}")
        elif msg_type == "IMAGE":
            if len(parts) >=4:
                author = parts[1]
                filename = parts[2]
                b64_img = parts[3]
                try:
                    img_data = base64.b64decode(b64_img)
                    pil_img = Image.open(io.BytesIO(img_data))
                    ctk_img = CTkImage(pil_img,size=(300,300))
                    self.add_message(f"{author}{filename}", img=ctk_img)
                except Exception as e:
                    self.add_message(f"Помилка зображення: {e}")
        else:
            self.add_message(line)
    def save_name(self):
        new_name = self.entry.get()
        if new_name:
            self.username = new_name
            self.add_message(f"Ваш новий нік:{self.username}")





    

        
            















reg_win = Registerwindow()
reg_win.mainloop()
