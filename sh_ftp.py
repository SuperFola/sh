from ftplib import FTP
from getpass import getpass
from os import path
import os
from glob import glob


def store(connection, *args):
    "Store a file (opened in binary mode) specified by the user"
    filenames = input("Filename(s) to store (use a single space to separate each filename) > ").split(" ") if not args else args
    for filename in filenames:
        if path.exists(path.join(curdir, filename)):
            fn_to_send = path.split(path.join(curdir, filename))[1]
            with open(path.join(curdir, filename), "rb") as fileobject:
                ret = connection.storbinary("STOR " + fn_to_send, fileobject)
                print(ret)
        else:
            print("[!] {} didn't exist in the current local working directory !".format(path.join(curdir, filename)))


def ls(connection, *args):
    """List the files in the current working directory
    if -local is the first argument, it will list all the files/folders in the current local directory
    """
    if not args:
        ret = connection.dir(*args)
    elif args[0] == '-local':
        ret = '\n- '.join(glob(curdir + "/*"))
    else:
        ret = connection.dir(*args)
    print(ret)


def del_(connection, *args):
    """Delete a file specified by the user
    if -local is the first argument, it will delete a fill from the current local directory"""
    loc = False
    if args:
        loc = True if args[0] == '-local' else False
        if loc:
            args.pop(0)
    to_del = input("File to delete > ") if not args else args[0]
    if not loc:
        ret = connection.delete(to_del)
    else:
        try:
            os.remove(to_del)
            ret = "Removed " + to_del + " from the current local directory"
        except OSError:
            ret = to_del + " seems not to exists in the current local directory " + curdir
    print(ret)


def ren(connection, *args):
    "Rename a file specified by the user"
    to_ren = input("Filename to change > ") if not args else args[0]
    new_name = input("New name for {} > ".format(to_ren)) if len(args) <= 1 else args[1]
    ret = connection.rename(to_ren, new_name)
    print(ret)


def mkd(connection, *args):
    """Make a new directory specified by the user
    if -local is the first argument, it will create a directory in the current local directory"""
    loc = False
    if args:
        loc = True if args[0] == '-local' else False
        if loc:
            args.pop(0)
    dir_name = input("New dir name > ") if not args else args[0]
    if not loc:
        ret = connection.mkd(dir_name)
    else:
        try:
            os.mkdir(dir_name)
            ret = "Created a directory " + dir_name + " in the current local directory"
        except OSError or NotImplementedError:
            ret = "Can not create the directory " + dir_name + " the current local directory"
    print(ret)


def cwd(connection, *args):
    """Change the current working directory
    if -local is the first argument, it will change the current local directory"""
    loc = False
    if args:
        loc = True if args[0] == '-local' else False
        if loc:
            args.pop(0)
    
    global curdir
    if loc:
        temp = input("Current local directory ? > ") if not args else args[0]
        if temp == '..':
            curdir, _ = path.split(curdir)
        if temp == '/':
            curdir = path.splitdrive(curdir if path.isabs(curdir) else path.join(getcwd(), curdir)) + os.sep
        print("Local working directory is " + curdir)
    else:
        new_cwd = input("New working directory > ") if not args else args[0]
        ret = connection.cwd(new_cwd)
        print(ret)


def cd(connection, *args):
    """Get the current working directory
    if -local is the first argument, it will print the current local directory path"""
    loc = False
    if args:
        loc = True if args[0] == '-local' else False
        if loc:
            args.pop(0)
    if not loc:
        ret = connection.pwd()
    else:
        ret = curdir
    print(ret)


def size(connection, *args):
    "Get the size of a filename specified by the user"
    filename = input("File to size > ") if not args else args[0]
    ret = connection.size(filename)
    print(ret)


def retrieve(connection, *args):
    "Get a file from the server"
    filename = input("File to download > ") if not args else args[0]
    ret = connection.retrbinary("RETR " + filename, open(path.join(curdir, filename), "wb").write)


def rmd(connection, *args):
    "Remove a directory specified by the user"
    dir_name = input("Directory to delete > ") if not args else args[0]
    ret = connection.rmd(dir_name)
    print(ret)


commands = {
    "store": store,
    "ls": ls,
    "del": del_,
    "ren": ren,
    "mkd": mkd,
    "cwd": cwd,
    "cd": cd,
    "size": size,
    "rmd": rmd,
    "retr": retrieve
}

def main():
    host = input("Host > ")
    port = 21
    user = input("User for {}:{} > ".format(host, port))
    password = getpass("Password for {} on {}:{} > ".format(user, host, port))
    debuglevel = 1
    curdir = os.getcwd()

    connection = FTP()
    try:
        connection.connect(host, port)
    except ConnectionRefusedError:
        print("Can not connect to {}:{}, connection was refused".format(host, port))
        return 1
    connection.login(user, password)
    connection.set_debuglevel(debuglevel)

    print("\n" + connection.getwelcome() + "\n")

    while True:
        usercommand = input("\n$ ")
        cmd, *args = usercommand.split(' ')
        
        if cmd in commands.keys():
            commands[cmd](connection, *args)
        elif cmd == "quit":
            break
        elif cmd == "help":
            for k, v in commands.items():
                print("\t- {} :\n{}\n".format(k, v.__doc__))
            print("\t- quit :\nClose the connection")
        else:
            print("Unrecognized command.")

    connection.quit()
    
    return 0


if __name__ == '__main__':
    main()