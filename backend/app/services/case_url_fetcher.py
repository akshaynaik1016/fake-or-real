"""Bounded public HTTP fetch with IP pinning and validation on every redirect."""
import asyncio
import http.client
import ipaddress
import socket
import ssl
import time
from urllib.parse import urljoin,urlsplit
from bs4 import BeautifulSoup
from app.security.ssrf import validate_and_resolve_url

MAX_BYTES=512*1024
MAX_REDIRECTS=3
TOTAL_TIMEOUT=15

class URLFetchError(Exception):
    def __init__(self,code,message):super().__init__(message);self.code=code


def validate_public_target(url,resolve=True):
    try:
        parsed=urlsplit(url)
        if parsed.scheme.lower() not in {'http','https'} or parsed.port not in {None,80,443}:
            raise URLFetchError('URL_BLOCKED','Only public HTTP/HTTPS destinations on ports 80/443 are allowed.')
        safe,message,addresses=validate_and_resolve_url(url,resolve_dns=resolve)
        if not safe:raise URLFetchError('URL_BLOCKED',message)
        if resolve and (not addresses or any(not ipaddress.ip_address(a).is_global for a in addresses)):
            raise URLFetchError('URL_UNRESOLVED','No validated public destination address is available.')
        return parsed,addresses
    except ValueError:
        raise URLFetchError('URL_BLOCKED','Malformed URL or port.')


class PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self,host,address,port,timeout):
        super().__init__(host,port=port,timeout=timeout,context=ssl.create_default_context());self.address=address
    def connect(self):
        self.sock=socket.create_connection((self.address,self.port),self.timeout)
        self.sock=self._context.wrap_socket(self.sock,server_hostname=self.host)


def open_connection(parsed,address,timeout):
    if parsed.scheme=='https':return PinnedHTTPSConnection(parsed.hostname,address,parsed.port or 443,timeout)
    return http.client.HTTPConnection(address,port=parsed.port or 80,timeout=timeout)


def fetch_public_text_sync(url,allow_pdf=False,allowed_domains=None):
    deadline=time.monotonic()+TOTAL_TIMEOUT;current=url;chain=[]
    for redirect in range(MAX_REDIRECTS+1):
        if allowed_domains:
            from app.services.notice_verification import trusted_host
            if not trusted_host(current,allowed_domains):raise URLFetchError('URL_REDIRECT_BLOCKED','Document retrieval left the independently established HTTPS website boundary.')
        parsed,addresses=validate_public_target(current,resolve=True)
        remaining=deadline-time.monotonic()
        if remaining<=0:raise URLFetchError('URL_TIMEOUT','URL fetch exceeded its time limit.')
        connection=open_connection(parsed,sorted(addresses)[0],min(4,remaining))
        try:
            path=parsed.path or '/'
            if parsed.query:path+='?'+parsed.query
            host=parsed.hostname.encode('idna').decode()
            if ':' in host:host='['+host+']'
            if parsed.port:host+=':'+str(parsed.port)
            connection.request('GET',path,headers={'Host':host,'User-Agent':'FakeOrRealInvestigation/1.0','Accept':'text/html,text/plain,application/pdf' if allow_pdf else 'text/html,text/plain','Accept-Encoding':'identity'})
            response=connection.getresponse();chain.append(current)
            if response.status in {301,302,303,307,308}:
                location=response.getheader('Location')
                if not location or redirect==MAX_REDIRECTS:raise URLFetchError('URL_REDIRECT_LIMIT','Redirect is missing a destination or exceeds the redirect limit.')
                current=urljoin(current,location)
                # The next iteration resolves and checks this destination before any connection.
                continue
            if not 200<=response.status<300:raise URLFetchError('URL_HTTP_ERROR','Remote page returned an unsuccessful status.')
            if response.getheader('Content-Encoding','identity').lower()!='identity':
                raise URLFetchError('URL_ENCODING_UNSUPPORTED','Compressed response rejected by the bounded fetcher.')
            mime=response.getheader('Content-Type','').split(';')[0].lower()
            if mime not in ({'text/html','text/plain','application/xhtml+xml','application/pdf'} if allow_pdf else {'text/html','text/plain','application/xhtml+xml'}):
                raise URLFetchError('URL_CONTENT_TYPE','URL did not return supported readable HTML/text.')
            limit=2*1024*1024 if allow_pdf and mime=='application/pdf' else MAX_BYTES
            length=response.getheader('Content-Length')
            if length and (not length.isdigit() or int(length)>limit):raise URLFetchError('URL_TOO_LARGE','URL response exceeds the bounded document size limit.')
            data=bytearray()
            while len(data)<=limit:
                remaining=deadline-time.monotonic()
                if remaining<=0:raise URLFetchError('URL_TIMEOUT','URL fetch exceeded its time limit.')
                if connection.sock:connection.sock.settimeout(min(4,remaining))
                chunk=response.read(min(16384,limit+1-len(data)))
                if not chunk:break
                data.extend(chunk)
            if len(data)>limit:raise URLFetchError('URL_TOO_LARGE','URL response exceeds the bounded document size limit.')
            if mime=='application/pdf':
                from app.documents.pdf_analyzer import analyze_pdf_document
                parsed_pdf=analyze_pdf_document(bytes(data),'independently-retrieved.pdf')
                if not parsed_pdf.get('num_pages') or not parsed_pdf.get('text','').strip():raise URLFetchError('URL_PDF_NO_TEXT','Retrieved PDF contained no readable text.')
                text=parsed_pdf['text']
            else:text=data.decode('utf-8',errors='replace')
            if mime not in {'text/plain','application/pdf'}:
                soup=BeautifulSoup(text,'html.parser')
                for element in soup(['script','style','noscript']):element.decompose()
                text=soup.get_text('\n',strip=True)
            if not text.strip():raise URLFetchError('URL_NO_TEXT','No readable text returned by the page.')
            return {'text':text[:50000],'final_url':current,'redirect_chain':chain,'truncated':len(text)>50000,'bytes_read':len(data),'content_type':mime}
        except URLFetchError:raise
        except (TimeoutError,socket.timeout):raise URLFetchError('URL_TIMEOUT','URL connection/read timed out.')
        except Exception:raise URLFetchError('URL_UNAVAILABLE','URL could not be retrieved securely.')
        finally:connection.close()


async def fetch_public_text(url,allow_pdf=False,allowed_domains=None):
    try:return await asyncio.wait_for(asyncio.to_thread(fetch_public_text_sync,url,allow_pdf,allowed_domains),timeout=TOTAL_TIMEOUT+1)
    except asyncio.TimeoutError:raise URLFetchError('URL_TIMEOUT','URL fetch exceeded its total time limit.')
