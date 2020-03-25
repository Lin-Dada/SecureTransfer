### 文件安全传输系统

#### 环境说明
> 注：本系统服务器没有部署在云端，需在本地启动执行

- 操作系统：Win10
- 编程语言：Python3.6
- 依赖Python库：tkinter、pymysql、ssl、socket等（大多均为Python内置）
- mysql中应先建立数据库：filetransfer，新建表user，含有三个字段：id、username、password
- 启动方法：
	-   启动服务器：
```
    -   python server_ssl.py 
    -   python server_no_ssl.py
```
2）	启动客户端：
`python main.py`

#### 文件夹说明
- cer -- 该文件夹存放了CA根证书及服务器、客户端证书（使用OpenSSL生成）
    -   CA -- 根证书及秘钥
    -   server -- 服务器秘钥、代签名证书及已签名证书
    -   client -- 客户端秘钥、代签名证书及已签名证书
- ClientCache -- 该目录存放向服务器请求更新的下载列表数据
- ClientDownload -- 客户端下载路径
- ServerRec -- 服务器上传路径

#### 文件说明
- main.py 客户端启动文件
- client_login.py 客户端登录界面
- client_mian.py 客户端主界面
- view.py 客户端主界面视图
- client_socket_no_ssl.py 客户端不加密通信对象
- client_socket_ssl.py 客户端加密通信对象
- server_no_ssl.py 服务器不加密通信代码
- server_ssl.py 服务器加密不加密通信代码
- result.txt 用来记录服务器的下载列表
- Serverlog.txt 服务器日志
- 

#### 自定义传输协议
在服务器与客户端的每次交流都添加了自定义报头，客户端主动向服务器请求数据，服务器被动返回，因此两者的数据包头会不同。本系统使用了python的struct结构体实现了报头二进制流的传输。

客户端的报头内容如下：（1024字节）
- Command包括：Download、Upload、Update、Login和Register
- filename在download指令下是要下载的文件名，在Upload模式下是本地上传文件的路径。
- filesize是文件的大小
- time是数据请求的时间
- user和password是用户名和密码，每次请求数据都会验证一次，模拟Cookie模式。
```python
header = {
            'Command': 'Download',
            'fileName': filename,
            'fileSize': '',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'user': self.username,
            'password': self.password,
        }
```
服务器的报头内容如下：（128字节）

由于服务器是被动地回复客户端，所以报头内容不需要太多，故使用128字节。
- Feedback指示要回应的指令
- Stat指示响应的状态（如注册、登录等）
- Filesize是文件的大小
- User是当前用户
```python
header = {
                'Feedback': 'Login',
                'stat': 'Success',
                'fileSize': os.stat(listResult).st_size,
                'user': username
             }
```