import email, imaplib
import zmq
import random
import datetime, time

volume = '0.1'
user = ''
pwd = ''

c = zmq.Context()

print("Connecting to the mt4 server...")
s = c.socket(zmq.REQ)
s.connect("tcp://127.0.0.1:5557")

r = c.socket(zmq.PULL)
r.connect("tcp://127.0.0.1:5558")


def generate_nonce(length=8):
    """Generate pseudorandom number."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


def trade(signal,volume,pair):
    try:
        trade = 'TRADE|OPEN|' + signal + '|' + pair + '|0|0|0|IcarusBot Trade|' + generate_nonce() + '|' + volume
        s.send_string(trade, encoding='utf-8')
        print("Waiting for metatrader to respond...")
        m = s.recv()
        print("Reply from server ", m)
    except Exception as e:
        print(e)
print("Listening to email server...")


def readmail(volume):
    #print("Sleeping 3 Seconds")
    time.sleep(1.5)

    m = imaplib.IMAP4_SSL("imap.gmail.com")
    m.login(user, pwd)
    m.select('"[Gmail]/All Mail"')
    day = time.strftime("%d")
    resp, items = m.search(None,
                           "NOT SEEN FROM tradingview SENTON " + day + "-JUN-2018")
    items = items[0].split()
    for emailid in items:
        resp, data = m.fetch(emailid,
                             "(RFC822)")
        email_body = data[0][1]
        mail = email.message_from_bytes(email_body)

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        try:
            pair = mail['Subject'].split()[2]
            if mail['Subject'].split()[3] == "Buy":
                m.store(emailid, '+FLAGS', '\Seen')
                print(st + ' \x1b[6;30;42m' + 'Buy' + '\x1b[0m' + ' Triggered on ' + pair)
                trade('0', volume, pair)
            if mail['Subject'].split()[3] == "Sell":
                m.store(emailid, '+FLAGS', '\Seen')
                print(st + ' \x1b[6;30;41m' + 'Sell' + '\x1b[0m' + ' Triggered on ' + pair)
                trade("1", volume, pair)
        except Exception as e:
            print(e)


while True:
    readmail(volume)
