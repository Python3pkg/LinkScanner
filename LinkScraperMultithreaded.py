import requests
import string
import threading
from collections import deque
from time import sleep

class peekQueue(deque):
    def __init__(self):
        self.lock=threading.Lock()
    def tolist(self):
        return list(self)
    def isEmpty(self):
        return False if len(self) > 0 else True
    def peek(self,index=0):
        index=int(index)
        try:
            return self.tolist()[index]
        except:
            return (None,1)
class Scanner:
    def __init__(self,siteList='siteList.txt',iterations=2,maxthreads=8):
        self.recursion=iterations
        self.linkqueue=peekQueue()
        self.maxthreads=maxthreads
        self.siteList=self.loadSites(siteList)
        print("Sitelist:"+str(self.siteList))
        self.output=[]

    def loadSites(self,sitefilename):
        with open(str(sitefilename),'r') as siteListf:
            siteList = siteListf.read().split(",")
            siteListf.close()
        return siteList

    def getAllLinks(self,html):
        links = []
        start = html.find('href="')
        end = html.find('"', start + 6)
        while True:
            if start == 5:
                print(links)
                try:
                    del links[-1]
                except:
                    pass
                break
            else:
                start = html.find('href="') + 6
                end = html.find('"', start)
                link = html[start:end]
                if 'http://' in link:
                    links.append(link)
                elif 'https://' in link:
                    links.append(link)
                elif '//' in link:
                    links.append('http:'+link)
                html = html[end:]
        return links
    def isValidURL(self,url):
        if "mailto:" in str(url):
            return False
        else: return True

    def startScan(self):
        self.linkqueue.extendleft([(x,1) for x in self.siteList])
        print(self.linkqueue.tolist())
        while not self.linkqueue.peek(0)[1] > self.recursion:
            if (len(threading.enumerate()) <=self.maxthreads) and not self.linkqueue.isEmpty():
                p=threading.Thread(target=self.scan)
                p.start()
                print("Thread Added!")
            elif len(threading.enumerate()) >=self.maxthreads:
                threading.enumerate()[-1].join()
                print("{} Threads Reached!".format(len(threading.enumerate())))
            else: sleep(1)


    def scan(self):
        with self.linkqueue.lock:
            url,tasknum = self.linkqueue.pop()
        if "mailto:" not in str(url):
            r = requests.get(url)
            links = self.getAllLinks(r.text)
            for x in links:
                self.linkqueue.appendleft((x,tasknum+1))
            self.output=self.output+links
        else: pass
    def save(self,filename='links.txt'):
        print("Saving...")
        with open(filename,"w+") as linksf:
            linksf.write('\n'.join(map(str,self.output)))
            linksf.close()
print('Hello!')
if __name__=='__main__':
    linkscanner=Scanner(iterations=3,maxthreads=20)
    linkscanner.startScan()
    linkscanner.save()