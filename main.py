import socket
from bs4 import BeautifulSoup
from urllib.parse import urlencode

def parser_html(text):
    soup = BeautifulSoup(text, "html.parser")
    result = {}
    code = []
    for table in soup.find("table").find_all("code"):
        code.append(table.text)
    for i in range(0, len(code), 2):
        result[code[i]] = code[i + 1]
    return result


def parser_html_route(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.find("code").text


def parser_html_route_teg_a(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.find("a").get("href")


class requests:
    def __init__(self, host):
        self.host = host

    def response(self, socket_request):
        result = b""
        while True:
            chunk = socket_request.recv(4096)
            if not chunk:
                break
            result += chunk
        return result.decode("utf-8", errors="replace")

    def GET(self, cookies={}, params={}, path="/", headers={}):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, 80))

        cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        params_str = "?" + urlencode(params) if params else ""

        request = (
            f"GET {path + params_str} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"Cookie: {cookies_str}\r\n"
            f"{headers_str}"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("utf-8"))
        response = self.response(sock)
        sock.close()
        return response

    def POST(self, cookies={}, params={}, path="/", headers={}, data={}):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, 80))

        cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
        headers_str = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
        params_str = "?" + urlencode(params) if params else ""
        body_data = urlencode(data).encode("utf-8")

        request = (
            f"POST {path + params_str} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"Cookie: {cookies_str}\r\n"
            f"Content-Type: application/x-www-form-urlencoded\r\n"
            f"{headers_str}"
            f"Content-Length: {str(len(body_data))}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("utf-8") + body_data)
        response = self.response(sock)
        sock.close()
        return response

    def POST_FILES(self, cookies={}, path="/", files={}):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, 80))

        cookies_str = "; ".join(f"{k}={v}" for k, v in cookies.items())

        body = b""
        for fname, content in files.items():
            content_bytes = content.encode("utf-8")
            body += (
                f"--Boundary\r\n"
                f'Content-Disposition: form-data; name="file"; filename="{fname}"\r\n'
                f"Content-Type: text/plain\r\n"
                f"\r\n"
            ).encode("utf-8")
            body += content_bytes+b"\r\n"
        body += f"--Boundary--\r\n".encode("utf-8")

        request = (
            f"POST {path} HTTP/1.1\r\n"
            f"Host: {self.host}\r\n"
            f"Cookie: {cookies_str}\r\n"
            f"Content-Type: multipart/form-data; boundary=Boundary\r\n"
            f"Content-Length: {len(body)}\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode("utf-8") + body)
        response = self.response(sock)
        sock.close()
        return response


ID = "908f4d71a61883c70a9081215d69fab9"
request = requests("hw1.alexbers.com")
result_html = request.GET(cookies={"user": ID})

request_count = 0
while True:
    cookies = {}
    params = {}
    headers = {}
    body = {}
    request_count += 1
    if "При переходе выставьте следующие параметры запроса, указанные в таблице:" in result_html:
        params = parser_html(
            result_html[result_html.find("При переходе выставьте следующие параметры запроса, указанные в таблице:"):])
    if "Запрос должен иметь следующие заголовки:" in result_html:
        headers = parser_html(result_html[result_html.find("Запрос должен иметь следующие заголовки:"):])
    if "Запрос должен иметь следующие данные формы:" in result_html:
        body = parser_html(result_html[result_html.find("Запрос должен иметь следующие данные формы:"):])
    if "В запросе должны быть выставлены cookie:" in result_html:
        cookies = parser_html(result_html[result_html.find("В запросе должны быть выставлены cookie:"):])
    cookies["user"] = ID
    try:
        if "Отправьте GET-запрос" in result_html:
            rout_url = parser_html_route(result_html[result_html.find("Отправьте GET-запрос"):])
            result_html = request.GET(path=rout_url, cookies=cookies, params=params, headers=headers)
        elif "Отправьте POST-запрос" in result_html:
            rout_url = parser_html_route(result_html[result_html.find("Отправьте POST-запрос"):])
            result_html = request.POST(path=rout_url, cookies=cookies, params=params, headers=headers, data=body)
        elif "Загрузите файлы по адресу" in result_html:
            rout_url = parser_html_route(result_html[result_html.find("Загрузите файлы по адресу"):])
            files_dict = parser_html(result_html)
            result_html = request.POST_FILES(path=rout_url, cookies=cookies, files=files_dict)
        elif "Перейдите по" in result_html:
            rout_url = parser_html_route_teg_a(result_html[result_html.find("Перейдите по"):])
            result_html = request.GET(path=rout_url, cookies=cookies, params=params, headers=headers)
        else:
            print(result_html)
            break
    except OSError:
        request_count -= 1

print(f"Запросов:{request_count}")
