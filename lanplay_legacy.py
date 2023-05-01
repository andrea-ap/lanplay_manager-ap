import os, requests, json, re
import threading
from tkinter import *
from db import database


class App(Frame):

    server_address = None
    add_server_win = None
    list_box = None
    thread = None

    tids = None

    graphql_request = {"query": """
        query {
            serverInfo {
                online,
                idle,
                version
            }
            room {
                ip
                contentId,
                hostPlayerName,
                sessionId,
                nodeCountMax,
                nodeCount,
                nodes {playerName,nodeId,isConnected}
                advertiseDataLen,
                advertiseData
            }
        }
    """}

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.server_address = StringVar()
        self.parent = parent
        self.parent.geometry('350x200')
        self.parent.attributes('-topmost', False)
        self.tids = json.loads(open('lib/assets/games.json').read())
        self.generate_gui()

    def generate_gui(self):
        # Main window and title
        self.parent.title(window_title_label)

        # Menu bar and drop down ADD
        menu = Menu(self.parent, tearoff=0)
        menu.add_command(label=launch_client_label, command=self.launch_server)
        menu.add_command(label=add_server_label, command=self.add_server)
        menu.add_command(label=delete_server_label, command=self.delete_server)
        menu.add_command(label=refresh_clients_label, command=self.refresh_server_list_thread)
        self.parent.config(menu=menu)

        # Server list
        self.load_server_list()

    def load_server_list(self):
        self.list_box = Listbox(self.parent, width=60, height=60)
        self.list_box.pack(side='left', fill='y')

        scrollbar = Scrollbar(self.parent, orient="vertical", command=self.list_box.yview)
        scrollbar.pack(side="right", fill="y")

        self.list_box.config(yscrollcommand=scrollbar.set)

        # Load all server register
        self.refresh_server_list()

  

        

    def launch_server(self):
        if self.check_selected_server():
            server_selected = self.check_selected_server()
            if self.check_server_status(server_selected, True):
                command = "start /B start cmd.exe @cmd /k bin\lan-play.exe --relay-server-addr %s" % server_selected
                os.system(command)

    def delete_server(self):
        if self.check_selected_server():
            server_selected = self.check_selected_server()
            db = database()
            db.delete_server(server_selected)
            db.close_connection()
            self.list_box.delete(self.list_box.curselection())
            messagebox.showinfo(oops_label, server_deleted_label)

    def check_server_status(self, server_address, show_message):
        """
        Check the server status and returns players online
        :param show_message:
        :param server_address:
        :return:
        """
        status = {}


        url = "http://%s" % server_address
        res = requests.post(url, json=self.graphql_request)
        print(server_address)
        if (res.status_code == 200):
            data = json.loads(res.text)['data']
            status['online'] = int(data['serverInfo']['online'])
            status['idle'] = int(data['serverInfo']['idle'])
            status['rooms'] = data['room']
            return status
        

        url = "http://%s/info" % server_address
        res = requests.get(url)
        if (res.status_code == 200):
            data = json.loads(res.text)
            status = {}
            if ('online' in data):
                status['online'] = int(data['online'])

        url = "http://%s" % server_address
        res = requests.get(url)
        if (res.status_code == 200):
            try:
                data = json.loads(res.text)
                if 'clientCount' in data:
                    status['online'] = int(data['clientCount'])
            except:
                pass

        if (not 'online' in status):
            status['online'] = "?"

        if show_message:
            messagebox.showinfo(oops_label, server_no_reponse_label)

        return status

    def check_selected_server(self):
        try:
            index = self.list_box.curselection()[0]
            server_selected = self.list_box.get(index)
            while (server_selected.startswith('    ')):
                index -= 1
                server_selected = self.list_box.get(index)
            server_selected = server_selected.split("]")[1].strip()
        except Exception:
            server_selected = None

        if server_selected:
            return server_selected

        messagebox.showinfo(oops_label, select_server_label)

    def do_popup(self, event):
        self.popup_menu.post(event.x_root, event.y_root)

    def add_server(self):
        self.add_server_win = Toplevel(self.parent)
        self.add_server_win.title(add_server_label)
        self.add_server_win.geometry("250x100")
        self.add_server_elements()

    def add_server_elements(self):
        input_server = Entry(self.add_server_win, width=40, textvariable=self.server_address)
        input_server.pack(expand="yes", anchor="center")

        enter_button = Button(self.add_server_win, text=save_label, font=(24), command=self.save_server)
        enter_button.pack(expand="yes", anchor="center")

    def save_server(self):
        if not self.server_address.get():
            messagebox.showinfo(oops_label, sever_address_value_label, parent=self.add_server_win)
        else:
            server_address = self.server_address.get()
            pattern = re.compile("^(?!http:|https:|www.)([-a-zA-Z0-9@:%._]{1,256}):([0-9]{1,5})$")

            if pattern.match(server_address):
                port_server = int(server_address.split(":")[1])

                if port_server < 0 or port_server > 65535:
                    messagebox.showinfo(great_label, server_port_values_label)
                elif self.check_server_status(server_address, True):
                    clients_online = self.check_server_status(server_address, False)
                    # Object db
                    db = database()
                    # Check if already exists
                    rows = db.select_server(server_address)
                    if rows:
                        messagebox.showinfo(great_label, server_already_exists_label)
                    else:
                        db.insert_server(server_address)
                        self.list_box.insert(END, self.generate_list_register(server_address, clients_online))
                        messagebox.showinfo(great_label, server_added_label)
                        self.add_server_win.destroy()
                    db.close_connection()
            else:
                messagebox.showinfo(great_label, server_address_example_label)


    def refresh_server_list_thread(self):
        thread1 = threading.Thread(target=self.refresh_server_list)
        thread1.start()

    def refresh_server_list(self):
        self.list_box.delete(0, END)

        db = database()
        rows = db.select_server('')
        db.close_connection()

        for row in rows:
            server_address = str(row[1])
            server_status = self.check_server_status(server_address, False)
            online = server_status['online']
            self.list_box.insert(END, f"[Online: {online}{' / Idle: ' + str(server_status['idle']) if ('idle' in server_status) else '' }]   {server_address}")
            if (('rooms' in server_status) and server_status['rooms'] != None):
                for room in server_status['rooms']:
                    self.list_box.insert(
                        END,
                        f"              {self.lookup_tid(room['contentId'])}: {room['nodeCount']}/{room['nodeCountMax']}"
                    )
                    self.list_box.insert(END, '    ')
    def lookup_tid(self, tid):

        for game in self.tids:
            if (tid.lower() == game['ID'].lower()):
                return game['Name']

        return "Unknown Game"

# Main labels
window_title_label = "Lanplay Manager Legacy"

# Menu labels
add_server_label = "Add server"
close_program_label = "Close program"

# Elements labels
launch_client_label = "Launch client"
select_server_label = "Please, select a server first."
server_no_reponse_label = "Server does not respond!"
delete_server_label = "Delete server"
server_deleted_label = "Server deleted!"
server_rooms_label = "              %s"
refresh_clients_label = "Refresh"

# Add server labels
save_label = "Save"
oops_label = "Oops!"
great_label = "Great!"
server_added_label = "Server added!"
sever_address_value_label = "Sever address cannot be empty!"
server_already_exists_label = "Server already exists!"
server_port_values_label = "Server port must be between 0 and 65535"
server_address_example_label = "Server address must be like lan.teknik.app:11451 for example"


def main():
    # Object db
    db = database()
    db.close_connection()

    # Window instance
    root = Tk()
    root.iconbitmap("lib/assets/lan.ico","lib/assets/lan.ico")
    App(root)
    # Main loop
    root.mainloop()


if __name__ == '__main__':
    main()