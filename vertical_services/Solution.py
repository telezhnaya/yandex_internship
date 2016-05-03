from collections import defaultdict


class KeyDict(defaultdict):
    def __missing__(self, key):
        ret = self[key] = self.default_factory(key)
        return ret


with open('unix.mailbox', mode='rb') as file:
    files = KeyDict(lambda x: open(x + '.mailbox', 'wb'))
    author = None
    for line in file:
        if line.startswith(b'From '):
            author = line.split(b' ', 2)[1].decode('utf-8')
        files[author].write(line)

    for f in files.values():
        f.close()
