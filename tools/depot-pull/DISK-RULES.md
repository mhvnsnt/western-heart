# DISK RULES — mandatory for every agent

The VM disk has filled up before and blocked all work. These rules are not
optional.

1. **Check before you pull.** Run `df -h` first. Keep at least 10 GB free at
   all times. If a pull would break that, STOP and ask.
2. **Never download a full game.** Use `depot-pull.sh get` with a filelist.
   If you need "everything," you don't — narrow the filelist and pull in
   passes, extracting and deleting between passes.
3. **Extract, convert, delete.** Paks are a means, not an end. Once you've
   exported what you need to FBX/GLB, delete the downloaded paks.
4. **Scratch goes in `/tmp`, results go in the repo.** Don't accumulate
   multi-GB working copies in `~/workspace`.
5. **One game at a time.** Finish extracting game A before pulling game B.
6. **If the disk fills anyway:** stop your download immediately, delete your
   scratch downloads, and report it — don't wait for someone else to notice.
