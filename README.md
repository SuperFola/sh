# sh 
A simple Python (3.x) shell working with environments to be in several directories with only one shell.

The default environment is not named, so you can call it by using `! your command`

Typing `!name` will cause to go in the directory linked to the environment named `name`, and you won't have to type `!name` in front of your commands while you stay in the directory.

Example :

```
f:\stuff\sh$ show env

f:\stuff\sh$ newenv unr ..\..\ENDIVE
f:\stuff\sh$ newenv ae ..\..\AEngine\project
f:\stuff\sh$ !unr git status
On branch master
Your branch is up-to-date with 'origin/master'.
nothing to commit, working tree clean
f:\ENDIVE$ !ae
f:\AEngine\project$ ! git status
On branch master
Your branch is up-to-date with 'origin/master'.
Untracked files:
  (use "git add <file>..." to include in what will be committed)

        README.md

nothing added to commit but untracked files present (use "git add" to track)
f:\stuff\sh$ show env
                      ae                    unr
f:\stuff\sh$
```

For more commands, start the shell and type `help`