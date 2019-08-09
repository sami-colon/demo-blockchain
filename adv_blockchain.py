from pickle import HIGHEST_PROTOCOL, dump, load
from hashlib import sha256
from os import stat, _exit, system

# opening datafile for further use.
blockchain_file, users_list_file, pass_list_file = None, None, None
try:
    blockchain_file = open("blockchain_data/blockchain.pkl", 'rb')
    users_list_file = open("blockchain_data/user_list.pkl", 'rb')
    pass_list_file = open("blockchain_data/pass_list.pkl", 'rb')
except FileNotFoundError:
    print("Data file not found! Try running again after having approprate files in the directory.")
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
    #return sha256(json.dumps(block).encode()).hexdigest()  # serialize json and then find sha256 hash of block!


def valid_proof(transactions, last_hash, nonce):
    guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
    guess_hash = sha256(guess).hexdigest()
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    nonce = 0
    while not valid_proof(open_transactions, last_hash, nonce):
        nonce += 1
    return nonce


def get_last_block():
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    users_list[recipient].amount += amount
    users_list[owner].amount -= amount
    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
    open_transactions.append(transaction)


# mine block
def mine_block():
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


def get_transaction_block():
    tx_recipient = input('Enter the recipient of the transaction: \n')
    tx_amount = float(input('Enter your transaction amount \n'))
    global owner
    if not users_list[owner].amount > tx_amount or tx_amount < 0:
        return False
    else:
        return tx_recipient, tx_amount


def get_user_choice():
    choice = input("Enter yout choice!\n")
    if not choice == "":
        return int(choice)
    else:
        return -1


def print_block():
    for block in blockchain:
        print("___________________________Here is your block_______________________________________________________")
        print()
        print(block)
        print("")


def register_user():
    name = input("Enter name \n").strip()
    pas = input("Enter Password \n").strip()
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
    else:
        print("User registered Successfuly ")


def set_owner(u):
    global owner
    owner = u


def select_account():
    u = input("Enter your username \n").strip()
    pas = input("Enter password \n").strip()
    try:
        if password_list[u] == pas:
            set_owner(u)
            print("User Logged in  : " + owner)
        else:
            print("wrong combination! ")
    except KeyError:
        print("No user Exists! ")
    return


def check_bal():
    print("You are "+owner)
    print(users_list[owner].amount)
    return


def save_object(obj, filename):
    with open(filename, 'wb') as fp:  # Overwrites any existing file.
        dump(obj, fp, HIGHEST_PROTOCOL)


while True:
    system('cls')
    print('_______________________________________________')
    print("Choose an option                               |")
    print('Choose 1 for adding a new transaction          |')
    print('Choose 2 for mining a new block                |')
    print('Choose 3 for printing the blockchain           |')
    print('Choose 4 to select your account                |')
    print('Choose 5 to register yourself.                 |')
    print('Choose 6 to see your account balance.          |')
    print('Choose anything else if you want to quit       |')
    print('_______________________________________________')
    user_choice = get_user_choice()
    if user_choice == 1:
        pas = input("Enter Password to continue! \n")
        if password_list[owner] == pas:
            tx_data = get_transaction_block()
            if not tx_data:
                print("Insuffiecient Funds! ")
                pass
            recipient, amount = tx_data
            try:
                temp = users_list[recipient]
                add_transaction(recipient,owner, amount=amount)
                print(open_transactions)
                input()
            except KeyError:
                print("No Such Recepient Exists Try again!")
                input()
                pass
        else:
            print("Wrong Credenetials !  Try selecting your account first.")
            input()

    elif user_choice == 2:
        if not len(open_transactions) == 0:
            mine_block()
            input()

    elif user_choice == 3:
        print_block()
        input()

    elif user_choice == 4:
        select_account()
        input()

    elif user_choice == 5:
        register_user()
        input()

    elif user_choice == 6:
        check_bal()
        input()

    elif user_choice == 7:
        print(users_list)
        print(password_list)
        input()

    else:
        system('cls')
        print("Saving current state of blockchain!")
        import time
        for i in range(7):
            time.sleep(1)
            print(". .. . .. . .. .")
        # writing data to local files!
        save_object(blockchain, "blockchain_data/blockchain.pkl")
        save_object(password_list, "blockchain_data/pass_list.pkl")
        save_object(users_list, "blockchain_data/user_list.pkl")
        system('cls')
        print('Data Writing completed!\n')

        exit(200)
        break
