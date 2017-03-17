import os
import glob
import pickle

import sh_ftp
import sh_index


help_message = """Help message here to ... help you !

environment related
    newenv name path   => creates a new environment named 'name', at 'path'
    saveenv            => saves all the environments in the .shells file

shell related
    quit               => quits the shell nicely
    help               => displays this message
    show index|env     => show all the indexes or environments available

ftp related
    ftp                => starts a ftp shell inside the shell

index related
    index path [ftype] => index all the files (recursively) at 'path',
                          matching ftype (if not given, match all files)
    search index kws   => search for kws in the index 'index'. enter q to
                          quit the display mode at any moment
"""


def template_out(template, lst_texts):
    out = []
    for text in lst_texts:
        if not len(out) or len(out[-1]) >= 3:
            out.append([template.format(text)])
        elif len(out[-1]) < 3:
            out[-1].append(template.format(text))
    return "\n".join("".join(i) for i in out)


def main():
    shells = {"": os.getcwd()}
    wd = os.getcwd()
    
    # on start-up
    if os.path.exists(".shells"):
        # loading the shells
        answ = input("Found saved shells. Do you want to load them [y/n] ? ")
        while answ.lower() not in ('y', 'n'):
            answ = input("[!] Incorrect input. Found saved shells. Do you want to load them [y/n] ? ")
        if answ.lower() == "y":
            shells = pickle.Unpickler(open(".shells", "rb")).load()
    
    while True:
        cmd, *args = input(os.getcwd() + "$ ").split(" ")
        
        # managing environment related commands
        if cmd[0] == "!":
            # we are using an environment
            cmd = cmd[1:]
            os.chdir(shells[cmd])
            # executing the command
            if args:
                if args[0] == "cd":
                    if args[1:]:
                        shells[cmd] = os.path.join(shells[cmd], args[1])
                    else:
                        print(shells[cmd])
                else:
                    os.system(" ".join(args))
        # env related
        elif cmd == "newenv":
            if len(args) <= 1:
                print("[!] Need more arguments. ex: newenv name path")
            else:
                shells[args[0]] = os.path.join(os.getcwd(), args[1])
        elif cmd == "saveenv":
            print("Saving all the environments (counted {})".format(len(shells)))
            pickle.Pickler(open(".shells", "wb")).dump(shells)
        # shell related
        elif cmd == "quit":
            print("Goodbye !")
            break
        elif cmd == "help":
            print(help_message)
        elif cmd == "show":
            if args:
                if args[0] == "index":
                    print(template_out("{:20}  ", [os.path.basename(file)[:-6] for file in glob.glob("indexes/*.index")]))
                elif args[0] == "env":
                    print(template_out("{:20}  ", sorted(shells.keys())))
                else:
                    print("Can not get what '{}' stands for".format(args[0]))
            else:
                print("[!] Need more arguments. ex: show index|env")
        # ftp related
        elif cmd == "ftp":
            sh_ftp.main()
        # index related
        elif cmd == "index":
            if len(args) <= 1:
                print("[!] Need more arguments. ex: index path [file type]")
            else:
                p = os.path.join(os.getcwd(), args[0])
                ftype = args[1] if args[1:2] else "*.*"
                print("This action is going to take a will. Registering files in {}".format(os.path.join(p, ftype)), flush=True)
                sh_index.index_all(p, ftype, wd)
        elif cmd == "search":
            if len(args) > 1:
                archive = os.path.join(wd, "indexes", args[0] + ".index")
                print("Searching in index at {}, will take a will".format(archive), flush=True)
                sh_index.search(archive, " ".join(args[1:]))
            else:
                print("[!] Need more arguments. ex: search index keywords..")
            # other
        else:
            os.system(cmd + " " + " ".join(args))


if __name__ == '__main__':
    main()