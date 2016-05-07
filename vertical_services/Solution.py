from collections import defaultdict


with open('unix.mailbox', 'rb') as file:
    author = None
    files = defaultdict(lambda: open('{}.mailbox'.format(author), 'wb'))
    for line in file:
        if line.startswith(b'From '):
            _, author, *_ = line.split(b' ', 2)
            author = author.decode('utf-8')
        files[author].write(line)

    for f in files.values():
        f.close()
