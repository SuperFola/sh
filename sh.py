#! python3
#coding: utf-8
import os
import sys
import glob
import pickle
import shutil

import sh_ftp
import sh_index


help_message = """Help message here to ... help you !

environment related
    new type (args)    => creates a new type with args
                          type can be : 'env', 'macro'
                          ex: new env name path
                              new macro (code..) 
                                         |________> batch/bash
    save type          => saves type in the appropriate file
                          type can be : 'env', 'macro'

shell related
    cd path            => change current directory to path
    rm (files)         => remove files
    quit               => quits the shell nicely
    help               => displays this message
    show type          => display the content of type
                          type can be : 'index', 'env', 'macro'

ftp related
    ftp                => starts a ftp shell inside the shell

index related
    index path [ftype] => index all the files (recursively) at 'path',
                          matching ftype (if not given, match all files)
    search index kws   => search for kws in the index 'index'. enter q to
                          quit the display mode at any moment
"""


def template_out(template, lst_texts):
    tsz = shutil.get_terminal_size((0, 0))
    X = tsz.columns // len(template.format("-"))
    out = []
    for text in lst_texts:
        if not len(out) or len(out[-1]) >= X:
            out.append([template.format(text)])
        elif len(out[-1]) < X:
            out[-1].append(template.format(text))
    return "\n".join("".join(i) for i in out)


def chdir(ndir):
    try:
        os.chdir(ndir)
    except FileNotFoundError:
        print("[!] Can not find directory {}".format(os.path.join(os.getcwd(), ndir)))


def splitscreen(macros, *args):
    tsz = shutil.get_terminal_size((0, 0))
    out = []
    if "," in args:
        args = " ".join(args).split(",")
        args = [a.strip(" ") for a in args]
    for a in args:
        if a[0] == ":":
            # we are using a macro
            a, *rgs = a[1:].strip(" ").split(" ")
            if a in macros.keys():
                out.append(os.popen(macros[a] + " " + " ".join(rgs)).read().replace('\r\n', '\n').replace('\r', '\n').split('\n'))
            else:
                print("[!] {} is not an existing macro".format(a))
        else:
            out.append(os.popen(a).read().replace('\r\n', '\n').replace('\r', '\n').split('\n'))
    sz = tsz.columns // len(out) - len(out)
    sformat = "{:" + str(sz) + "}"
    sformat = "|".join(sformat for _ in range(len(out)))
    a_line = lambda text, i: text[i] if i < len(text) else ""
    nout = []
    for text in out:
        ntext = []
        for line in text:
            tline = line
            while len(tline) >= sz:
                ntext.append(tline[:sz])
                tline = tline[sz:]
            ntext.append(tline)
        nout.append(ntext)
    out = nout[:]
    m = max(*[len(c) for c in out])
    for i in range(m):
        lines = [a_line(text, i) for text in out]
        print(sformat.format(*lines))


def parse_cmds_env(cmd, args, shells, macros, pymacros, wd):
    # we are using an environment
    cmd = cmd[1:]
    if cmd in shells:
        chdir(shells[cmd])
        # executing the command
        if args:
            if args[0] == "cd":
                if args[1:]:
                    shells[cmd] = os.path.join(shells[cmd], args[1])
                    chdir(shells[cmd])
                else:
                    print(shells[cmd])
            # handling macros
            else:
                cmd = args.pop(0)
                parse_commands(cmd, args, shells, macros, pymacros, wd)
    else:
        print("[!] {} is not an existing environment".format(cmd))


def parse_cmds_pymacros(cmd, args, shells, macros, pymacros, wd):
    # we are using a pymacro
    cmd = cmd[1:]
    if cmd in pymacros.keys():
        pymacros[cmd](macros, *args)
    else:
        print("[!] {} is not an existing python-macro".format(cmd))


def parse_cmds_macros(cmd, args, shells, macros, pymacros, wd):
    # we are using a macro
    cmd = cmd[1:]
    if cmd in macros.keys():
        os.system(macros[cmd] + " " + " ".join(args))
    else:
        print("[!] {} is not an existing macro".format(cmd))


def parse_cmds_new(cmd, args, shells, macros, pymacros, wd):
    if len(args) <= 1:
        print("[!] Need more arguments. ex: new type (args)")
    else:
        t = args.pop(0)
        if t == "env":
            try:
                os.chdir(os.path.join(os.getcwd(), " ".join(args[1:])))
            except FileNotFoundError:
                try:
                    os.chdir(" ".join(args[1:]))
                except FileNotFoundError:
                    print("[!] Could not create environment, invalid path")
                else:
                    shells[args[0]] = os.getcwd()
            else:
                shells[args[0]] = os.getcwd()
        elif t == "macro":
            macros[args[0]] = " ".join(args[1:])
            print(macros)
        else:
            print("[!] Can not create new '{}' because it is not recognized".format(t))


def parse_cmds_save(cmd, args, shells, macros, pymacros, wd):
    if not len(args):
        print("[!] Need more arguments. ex: save type")
    else:
        t = args.pop(0)
        if t == "env":
            print("Saving all the environments (counted {})".format(len(shells)))
            pickle.Pickler(open(os.path.join(wd, ".shells"), "wb")).dump(shells)
        elif t == "macro":
            print("Saving all the macros (counted {})".format(len(macros)))
            pickle.Pickler(open(os.path.join(wd, ".macros"), "wb")).dump(macros)
        else:
            print("[!] Can not save '{}' because it is not recognized".format(t))


def parse_cmds_show(cmd, args, shells, macros, pymacros, wd):
    if args:
        if args[0] == "index":
            print(template_out("{:20}  ", [os.path.basename(file)[:-6] for file in glob.glob("indexes/*.index")]))
        elif args[0] == "env":
            print(template_out("{:20}  ", sorted(shells.keys())))
        elif args[0] == "macro":
            print(template_out("{:20}  ", sorted(macros.keys())))
        else:
            print("Can not get what '{}' stands for".format(args[0]))
    else:
        print("[!] Need more arguments. ex: show index|env|macro")


def parse_commands(cmd, args, shells, macros, pymacros, wd):
    # managing environment related commands
    if cmd[0] == "!":
        parse_cmds_env(cmd, args, shells, macros, pymacros, wd)
    # managing pymacros (hard coded of course)
    elif cmd[0] == "#":
        parse_cmds_pymacros(cmd, args, shells, macros, pymacros, wd)
    # managing macros related commands
    elif cmd[0] == ":":
        parse_cmds_macros(cmd, args, shells, macros, pymacros, wd)
    # env related
    elif cmd == "new":
        parse_cmds_new(cmd, args, shells, macros, pymacros, wd)
    elif cmd == "save":
        parse_cmds_save(cmd, args, shells, macros, pymacros, wd)
    # shell related
    elif cmd == "cd":
        if len(args):
            chdir(" ".join(args))
        else:
            print("[!] Need more arguments. ex: cd directory")
    elif cmd == "rm":
        if args:
            for e in args:
                os.remove(e)
        else:
            print("[!] Need more arguments. ex: rm (files)")
    elif cmd == "help":
        print(help_message)
    elif cmd == "show":
        parse_cmds_show(cmd, args, shells, macros, pymacros, wd)
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
    elif cmd:
        os.system(cmd + " " + " ".join(args))


def main(*args):
    shells = {"": os.getcwd()}
    macros = {}
    pymacros = {"split": splitscreen}
    wd = os.getcwd()
    
    # on start-up
    if os.path.exists(".shells"):
        # loading the shells
        shells = pickle.Unpickler(open(".shells", "rb")).load()
    if os.path.exists(".macros"):
        # loading the macros
        macros = pickle.Unpickler(open(".macros", "rb")).load()
    
    if args:
        parse_commands(args[0], args[1:], shells, macros, pymacros, wd)
    
    while True:
        cmd, *args = input(os.getcwd() + "$ ").split(" ")
        if not cmd:
            continue
        
        if cmd == "quit":
            print("Goodbye !")
            break
        parse_commands(cmd, args, shells, macros, pymacros, wd)
        
        cmd, args = "", []


if __name__ == '__main__':
    args = []
    if sys.argv:
        args = sys.argv[1:]
    main(*args)

















