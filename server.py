import socket
import sys
import os


# find the path of the file inside the message from the client
def filepathfinder(datastr):
    HTTPIndex = dataStr.find("HTTP")
    # slicing the path of the file we want to search
    filepath = dataStr[4:HTTPIndex - 1]
    # in case file name is only '/' switch to index.html
    if filepath == "/":
        filepath = "/index.html"
    return filepath


# find the connection status inside the message from the client
def connectionfinder(datastr):
    connectionstatus = dataStr.find("keep-alive")
    if connectionstatus == -1:
        return "close"
    return "keep-alive"


# find if the file type is ico or jpg
def binaryfiletype(filepath):
    isjpgfile = filepath.find(".jpg")
    isicofile = filepath.find(".ico")
    if isjpgfile != -1 or isicofile != -1:
        return True
    else:
        return False


# read the file binary from the the computer
def readbinaryfromfile(filepath):
    path = os.getcwd() + "/files" + filepath
    fileptr = open(path, "rb")
    filedata = fileptr.read()
    fileptr.close()
    return filedata


# read the file from the the computer
def readstringfromfile(filepath):
    path = os.getcwd() + "/files" + filepath
    fileptr = open(path, "r")
    filedata = fileptr.read()
    fileptr.close()
    return filedata.encode()


# creating the found message
def filefound(connectionstatus, size):
    foundmessage = "HTTP/1.1 200 OK\nConnection: " + connectionstatus + "\nContent-length: " + str(size) + "\n\n"
    return foundmessage


# creating the not found message
def filenotfound():
    notfoundmessage = "HTTP/1.1 404 Not Found\nConnection: close" + "\n\n"
    return notfoundmessage


# creating the redirect message
def fileredirect():
    redirectmessage = "HTTP/1.1 301 Moved Permanently\nLocation: /result.html" + "\n\n"
    return redirectmessage

def isfileredirect(filepath):
    if filepath == "/redirect":
        return True
    return False


TCP_IP = '10.0.2.15'
TCP_PORT = int(sys.argv[1])

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((TCP_IP, TCP_PORT))

server.listen(1)

while True:
    client_socket, client_address = server.accept()
    client_socket.settimeout(1)
    try:
        while True:
            data = ""
            # data extraction loop
            while True:
                byte = client_socket.recv(1)
                data = data + byte.decode('utf-8')
                if data.find("\r\n\r\n") != -1:
                    break
            # in case the message from the client is empty
            if sys.getsizeof(data) == 0:
                client_socket.close()
                break
            # converting bytes to string
            dataStr = data
            # finding the file path and connection
            filepath = filepathfinder(dataStr)
            connectionstatus = connectionfinder(dataStr)
            # message variable
            message = None
            # check if client ask redirect
            isredirect = isfileredirect(filepath)
            if isredirect == True:
                message = fileredirect().encode()
                connectionstatus = "close"
            # checking if the file type is jpg or ico or regular
            isbinaryfile = binaryfiletype(filepath)
            # checking if file exist in the folder
            pathwithfiles = "files" + filepath
            realpath = os.path.realpath(pathwithfiles)
            isfileexist = os.path.exists(realpath)

            if isfileexist == True and isredirect == False:
                datatosend = None
                if isbinaryfile == True:
                    datatosend = readbinaryfromfile(filepath)
                else:
                    datatosend = readstringfromfile(filepath)

                message = filefound(connectionstatus, len(datatosend)).encode() + datatosend

            if isfileexist == False and isredirect == False:
                message = filenotfound().encode()
                connectionstatus = "close"

            client_socket.send(message)
            if connectionstatus == "close":
                client_socket.close()
                break

    except:
        client_socket.close()
        continue
