#coding: utf-8
import os
import glob
import pickle


MAXSIZE = 30


def index_all(path, ftype, wd):
    index = {}
    def _index(p, ftype):
        nonlocal index
        for file in glob.glob(os.path.join(p, ftype)):
            print(file, flush=True)
            index[file] = open(file, encoding='utf-8').read()
        for np in glob.glob(os.path.join(p, "*")):
            _index(np, ftype)
    _index(path, ftype)
    c = 0
    while len(index):
        i = 0
        new = {}
        keys = list(index.keys())
        for key in keys:
            new[key] = index.pop(key)
            i += 1
            if i == MAXSIZE:
                break
        pickle.Pickler(open(os.path.join(wd, "indexes", os.path.basename(path) + str(c) + ".part"), "wb")).dump(new)
        c += 1
    pickle.Pickler(open(os.path.join(wd, os.path.basename(path) + ".index"), "wb")).dump([os.path.basename(path) + str(k) + ".part" for k in range(c)])


def search(archive, kws):
    full_index = pickle.Unpickler(open(archive, "rb")).load()
    results = {}
    for f in full_index:
        temp = pickle.Unpickler(open(os.path.join(os.path.dirname(archive), f), "rb")).load()
        for ntemp, ftemp in temp.items():
            if kws in ftemp:
                fv = ftemp.replace("\r\n", "\n").replace("\r", "\n").split("\n")
                enc = []
                for i, line in enumerate(fv):
                    if kws in line:
                        enc.append(i - 4)
                        enc.append(i + 4)
                        break
                results[ntemp] = ["{:4}: {}".format(i + enc[0], fv[enc[0]:enc[1]][i]) for i in range(7)]
    display(results)


def display(r):
    for k, v in r.items():
        print(k, "\n".join(v), sep="\n" + "-" * len(k) + "\n")
        if input() == "q":
            break


def main():
    wd = os.getcwd()
    while True:
        cmd, *args = input(os.getcwd() + "$ ").split(" ")
        if cmd == "cd":
            os.chdir(os.path.join(os.getcwd(), " ".join(args)))
        elif cmd == "index":
            ftype = args[1] if args[1:2] else "*.*"
            p = os.path.join(os.getcwd(), args[0])
            print("This action is going to take a will. Registering files in {}".format(os.path.join(p, ftype)), flush=True)
            index_all(p, ftype, wd)
        elif cmd == "search":
            archive = os.path.join(wd, "indexes", args[0] + ".index")
            print("Searching in index at {}, will take a will".format(archive), flush=True)
            search(archive, " ".join(args[1:]))
        elif cmd == "lib":
            for file in glob.glob("indexes/*.index"):
                print(os.path.basename(file)[:-6])
        elif cmd == "help":
            print("Commands :")
            print("   cd path to change your current directory to path")
            print("   index directory [file type] to index all the files matching file type, in the directory specified")
            print("   search directory (keywords) to search in the archive directory.index for the keywords specified")
            print("   lib to display all the available indexes")
        elif cmd == "quit":
            break


if __name__ == '__main__':
    main()