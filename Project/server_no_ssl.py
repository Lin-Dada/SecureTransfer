import socket
import threading, struct, json, os, pymysql


#打开数据库连接
db = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='rootroot', db='fileTransfer',\
                     charset='utf8')
#使用cursor方法创建一个游标
cursor = db.cursor()
#查询数据库版本
cursor.execute("select version()")
data = cursor.fetchone()
print(" Database Version:%s" % data)

class server_ssl:
    def server_listen(self):
        # 监听端口
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as ssock:
            ssock.bind(('127.0.0.1', 6666))
            ssock.listen(5)
            while True:
                # 接收客户端连接
                connection, addr = ssock.accept()
                print('Connected by ', addr)
                #开启多线程,这里arg后面一定要跟逗号，否则报错
                thread = threading.Thread(target=self.conn_thread, args=(connection,))
                thread.start()

    def conn_thread(self,connection):
        while True:
            try:
                connection.settimeout(60)
                fileinfo_size = struct.calcsize('1024s')
                buf = connection.recv(fileinfo_size)
                if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
                    header_json = str(struct.unpack('1024s', buf)[0], encoding='utf-8').strip('\00')
                    #print(header_json)
                    header = json.loads(header_json)
                    Command = header['Command']

                    if Command == 'Upload':
                        fileName = header['fileName']
                        fileSize = header['fileSize']
                        time = header['time']
                        user = header['user']
                        filenewname = os.path.join('./ServerRec/', fileName)
                        print('Upload: file new name is %s, filesize is %s' % (filenewname, fileSize))
                        recvd_size = 0  # 定义接收了的文件大小
                        file = open(filenewname, 'wb')
                        print('start receiving...')
                        while not recvd_size == fileSize:
                            if fileSize - recvd_size > 1024:
                                rdata = connection.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = connection.recv(fileSize - recvd_size)
                                recvd_size = fileSize
                            file.write(rdata)
                        file.close()
                        print('receive done')

                        fileSize = float(fileSize)
                        if fileSize<1024.0:
                            fileSize = "%s bytes"%(int(fileSize))
                        elif fileSize/1024.0 <= 1024.0:
                            fileSize = "%.2f Kb"%(fileSize/1024.0)
                        elif fileSize/1024.0/1024.0 <= 1024.0:
                            fileSize = "%.2f Mb"%(fileSize/1024.0/1024.0)
                        else:
                            fileSize = "%.2f Gb"%(fileSize/1024.0/1024.0/1024.0)

                        uploadmsg = '{"文件名": "%s", "上传者": "%s", "上传时间": "%s", "大小": "%s"}\n'%\
                                    (fileName,user,time,fileSize)
                        with open('./result.txt','a',encoding='utf-8') as list:
                            list.write(uploadmsg)

                        uploadlog = '\n%s upload a file "%s" at %s' % \
                                        (user, fileName, time)
                        with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                            list.write(uploadlog)
                        #connection.close()

                    elif Command == 'Login':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s' and password = '%s'"%(username,password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            listResult = './result.txt'
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(listResult, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            print('%s login successfully')

                            loginlog = '\n%s try to login at "%s" , Stat: Success ' % \
                                        (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)
                            #connection.close()
                        else:
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Fail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to login at "%s" , Stat: Fail ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)

                    elif Command == 'Download':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s' and password = '%s'" % (username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        filename = header['fileName']
                        if data:

                            filepath = os.path.join('./ServerREc/', filename)
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Download',
                                'stat': 'Success',
                                'fileSize': os.stat(filepath).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(filepath, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            print('send file over...')
                            downloadlog = '\n%s download a file "%s" at %s' % \
                                          (username, filename, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(downloadlog)
                            # connection.close()
                        else:
                            header = {
                                'Feedback': 'Download',
                                'stat': 'LoginFail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                    elif Command == 'Update':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        sql = "select * from user where username = '%s' and password = '%s'" % (username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            listResult = './result.txt'
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Update',
                                'stat': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(listResult, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            #print('send list over...')
                            # connection.close()
                        else:
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Fail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                    elif Command == 'Register':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s'" % (username)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Register',
                                'stat': 'Exist',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to register at "%s" , Stat: Fail ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)
                        else:
                            sql = "insert into user values ('','%s','%s')"%(username,password)
                            cursor.execute(sql)
                            db.commit()
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Register',
                                'stat': 'Success',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to register at "%s" , Stat: Success ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)

            except socket.timeout:
                connection.close()
                break
            except ConnectionResetError:
                connection.close()
                break

if __name__ == "__main__":
    server = server_ssl()
    server.server_listen()