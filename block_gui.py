import tkinter
from hashlib import sha256
from os import stat, _exit
from pickle import HIGHEST_PROTOCOL, dump, load
# opening datafile for further use.
from time import sleep
from tkinter import messagebox

blockchain_file, users_list_file, pass_list_file = None, None, None
try:
    blockchain_file = open("blockchain_data/blockchain.pkl", 'rb')
    users_list_file = open("blockchain_data/user_list.pkl", 'rb')
    pass_list_file = open("blockchain_data/pass_list.pkl", 'rb')
except FileNotFoundError:
    print("Data file not found! Try running again after having approprate files. ")
    _exit(-11)


class User:
    name = ""
    amount = 0.0

    def register(self, name, amt):
        self.name = name
        self.amount = amt

    def transfer(self, amt):
        self.amount -= amt

    def receive(self, amt):
        self.amount += amt


reward = 1.0
open_transactions = []
owner = "Abhishek"
blockchain = []
password_list = {}
users_list = {}

# deserealising data from saved blockchain data.
if stat("blockchain_data/blockchain.pkl").st_size == 0:
    # genesis block
    genesis_block = {'previous_hash': '', 'index': 0, 'transaction': [{"Abhishek", "Abhishek", 100000000}], 'nonce': 23}
    blockchain = [genesis_block]  # write this to a file.
else:
    blockchain = load(blockchain_file)

# deserealising data from saved pass data.
if stat("blockchain_data/pass_list.pkl").st_size == 0:
    password_list = {owner: "password"}  # write this to a file.
else:
    password_list = load(pass_list_file)

# deserealising data from saved user data.
if stat("blockchain_data/user_list.pkl").st_size == 0:
    owner_user = User()
    owner_user.register(owner, 100000000)
    users_list = {owner: owner_user}  # write this to a file.  # write this to a file.
else:
    users_list = load(users_list_file)


def hash_block(block):
    return sha256(repr(sorted(block.items())).encode()).hexdigest()


def valid_proof(transactions, last_hash, nonce):
    guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
    guess_hash = sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash[0:2] == '00'


def get_last_block():
    return blockchain[-1]


def get_transaction_block():
    tx_recipient = input('Enter the recipient of the transaction: \n')
    tx_amount = float(input('Enter your transaction amount \n'))
    if not users_list[owner].amount > tx_amount or tx_amount < 0:
        return False
    else:
        return tx_recipient, tx_amount


def set_owner(u):
    global owner
    owner = u


def save_object(obj, filename):
    with open(filename, 'wb') as fp:  # Overwrites any existing file.
        dump(obj, fp, HIGHEST_PROTOCOL)


def check_bal():
    global win
    res = "User Info: ", "You are " + owner + "\n having a total of " + str(
        users_list[owner].amount) + " virtual coins!"
    messagebox.showinfo("User Info", res)
    print("You are " + owner)
    print(users_list[owner].amount)
    return


def print_block():
    global win
    messagebox.showinfo("Info", "Accessing Blockchain ledger and Printing!")
    for block in blockchain:
        print("___________________________Here is your block_______________________________________________________")
        print()
        print(block)
        print("\n")
    messagebox.showinfo("Info", "See Console Log for the stored Ledger!")


def proof_of_work():
    global win
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    nonce = 0
    while not valid_proof(open_transactions, last_hash, nonce):
        nonce += 1
    messagebox.showinfo("info", "Nonce Found = " + str(nonce))
    return nonce


def mine_block():
    global win
    if len(open_transactions) == 0:
        messagebox.showinfo("Info", "Nothing to mine, Add transactions first!")
    else:
        messagebox.showinfo("Info", "Mining the staged blocks! Wait for completion!")
        messagebox.showinfo("Info", "See Console Log for ongoing Process!")
        last_block = blockchain[-1]
        hashed_block = hash_block(last_block)
        nonce = proof_of_work()
        reward_transaction = {'sender': 'MINING', 'recipient': owner, 'amount': reward}
        users_list[owner].amount += reward
        open_transactions.append(reward_transaction)
        block = {
            'previous_hash': hashed_block,
            'index': len(blockchain),
            'transaction': open_transactions,
            'nonce': nonce
        }
        blockchain.append(block)
        open_transactions.clear()
        messagebox.showinfo("Info", "Mining Completed!")


def stringfy():
    ans = ""
    for x in open_transactions:
        l = list(x)
        amt = str(x[l[2]])
        ans += "sender: " + x[l[0]] + "  recipient: " + x[l[1]] + "  amount: " + amt + "\n"
    return ans


def add_transaction(recipient, sender=owner, amount=1.0):
    users_list[owner].amount -= amount
    users_list[recipient].amount += amount
    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
    open_transactions.append(transaction)


def verify(re, ta):
    global win
    if not users_list[owner].amount > ta or ta < 0:
        print("Insuffiecient Funds! ")
        messagebox.showerror("Error !", "Insufficient funds or wrong amount set")
    else:
        recipient, amount = re, ta
        try:
            x = users_list[recipient].name
            add_transaction(recipient, sender=owner, amount=amount)
            messagebox.showinfo("Completion!", "Transaction added sucesfully")
            print(open_transactions)
            res = stringfy()
            messagebox.showinfo("Transaction Pool so far", res)
            win.destroy()
            create_main_frame()
        except KeyError:
            print("No Such Recepient Exists Try again!")
            messagebox.showerror("Recpient error", "No Such Recepient Exists Try again!")


def add_trans():
    global win
    win.destroy()
    win = tkinter.Tk()
    win.title("transaction")
    win.geometry("350x250")
    win.resizable(False, False)
    win.title("Add Transaction")
    win.protocol("WM_DELETE_WINDOW", lambda: (win.destroy(), create_main_frame()))

    tkinter.Label(win, text="Enter Recepient name: ").place(x=40, y=50)
    tkinter.Label(win, text="Enter Amount").place(x=40, y=130)
    re = tkinter.StringVar()
    ta = tkinter.StringVar()
    tkinter.Entry(win, textvariable=re).place(x=190, y=50)
    tkinter.Entry(win, textvariable=ta).place(x=190, y=130)
    tkinter.Button(win, text="Add it to pooling zone", activebackground="pink", activeforeground="blue",
                   command=lambda: verify(re.get(), float(ta.get()))).place(x=40, y=170)


def close_system():
    # system('cls')
    global win
    mine_block()
    messagebox.showinfo("Saving Data", "Saving current state of blockchain!")
    print("Saving current state of blockchain!")
    import time
    for i in range(3):
        time.sleep(0.5)
        print(". .. . .. . .. .")
    # writing data to local files!
    save_object(blockchain, "blockchain_data/blockchain.pkl")
    save_object(password_list, "blockchain_data/pass_list.pkl")
    save_object(users_list, "blockchain_data/user_list.pkl")
    # system('cls')
    messagebox.showinfo("Saving Data", "Data Writing completed!")
    print('Data Writing completed!\n')
    win.destroy()
    exit(0)


def register(u, p):
    global win
    name = u
    pas = p
    flag = False
    try:
        temp = password_list[name]
    except KeyError:
        flag = True
        password_list[name] = pas
        u = User()
        u.register(name, 0.0)
        users_list[name] = u
        global owner
        owner = u
    if not flag:
        print("Username exists! Try again!\n")
        messagebox.showwarning("Info", "Username exists! Try again!\n")
    else:
        print("User registered Successfuly ")
        messagebox.showwarning("Info", "User registered Successfuly ")
        logout()


def register_user():
    global win
    win.destroy()
    win = tkinter.Tk()
    win.title("Register")
    win.geometry("300x250")
    win.protocol("WM_DELETE_WINDOW", lambda: logout())
    tkinter.Label(win, text="Username").place(x=30, y=50)
    tkinter.Label(win, text="Password").place(x=30, y=130)
    u = tkinter.StringVar()
    p = tkinter.StringVar()
    tkinter.Entry(win, textvariable=u).place(x=87, y=50)
    tkinter.Entry(win, textvariable=p).place(x=87, y=130)
    tkinter.Button(win, text="Register", activebackground="pink", activeforeground="blue",
                   command=lambda: register(u.get(), p.get())).place(x=30, y=170)
    win.mainloop()


def logout():
    global win
    win.destroy()
    win = tkinter.Tk()
    win.title("Login")
    win.geometry("250x220")
    win.resizable(False, False)
    tkinter.Label(win, text="Username").place(x=30, y=50)
    tkinter.Label(win, text="Password").place(x=30, y=130)
    u = tkinter.StringVar()
    p = tkinter.StringVar()
    tkinter.Entry(win, textvariable=u).place(x=87, y=50)
    tkinter.Entry(win, textvariable=p).place(x=87, y=130)
    tkinter.Button(win, text="Log In", activebackground="pink", activeforeground="blue",
                   command=lambda: select_account(u.get(), p.get())).place(x=30, y=170)
    tkinter.Button(win, text="Register ", activebackground="pink", activeforeground="blue",
                   command=lambda: register_user()).place(x=155, y=170)
    win.mainloop()


def logg():
    global win
    mine_block()
    messagebox.showinfo("Saving Data", "Saving current state of blockchain!")
    print("Saving current state of blockchain!")
    import time
    for i in range(3):
        time.sleep(0.5)
        print(". .. . .. . .. .")
    # writing data to local files!
    save_object(blockchain, "blockchain_data/blockchain.pkl")
    save_object(password_list, "blockchain_data/pass_list.pkl")
    save_object(users_list, "blockchain_data/user_list.pkl")
    # system('cls')
    messagebox.showinfo("Saving Data", "Data Writing completed!")
    print('Data Writing completed!\n')
    logout()


def create_main_frame():
    global win
    win = tkinter.Tk()
    win.geometry("350x370")
    win.resizable(False, False)
    win.title("Blockchain Demo")
    win.protocol("WM_DELETE_WINDOW", lambda: close_system())
    inf = tkinter.Label(win)
    inf.grid(row=0, column=0, columnspan=2)
    inf.config(text=f"Account Holder:- {str(owner)}")
    tkinter.Button(win, text="ADD Transaction\nto\nBlockchain", activebackground="green", activeforeground="blue",
                   command=lambda: add_trans()).grid(row=1, column=0, ipadx=20, ipady=20, padx=20, pady=40)
    tkinter.Button(win, text="Mine Block", activebackground="green", activeforeground="blue",
                   command=lambda: mine_block()).grid(row=1, column=1, ipadx=20, ipady=20, padx=20, pady=40)
    tkinter.Button(win, text="Print Blockchain", activebackground="green", activeforeground="blue",
                   command=lambda: print_block()).grid(row=2, column=0, ipadx=20, ipady=20, padx=20, pady=10)
    tkinter.Button(win, text="Show Balance!", activebackground="green", activeforeground="blue",
                   command=lambda: check_bal()).grid(row=2, column=1, ipadx=20, ipady=20, padx=20, pady=10)
    tkinter.Button(win, text="Logout!", activebackground="green", foreground='blue', background='red',
                   activeforeground="blue", command=lambda: logg()).grid(row=3, column=0, ipadx=10, ipady=10, padx=20,
                                                                           pady=10, columnspan=2)
    win.mainloop()


def select_account(u, pas):
    global win
    try:
        if password_list[u] == pas:
            set_owner(u)
            print("User Logged in  : " + owner)
            tkinter.messagebox.showinfo("Login Result!", "Login SuccessFull")
            global loggedIn
            loggedIn = True
            sleep(1)
            win.destroy()
            create_main_frame()
        else:
            print("wrong combination! ")
            tkinter.messagebox.showwarning("Login Result!", "wrong combination! \n Try again.")
    except KeyError:
        print("No user Exists! ")
        tkinter.messagebox.showwarning("Login Result!", "No user Exists! ")
    return


win = tkinter.Tk()
win.geometry("350x300")
logout()
