from urllib.parse import urlparse
import requests
from robots_parser import RobotsParser
from bs4 import BeautifulSoup
from typing import Self


class URLNode:
    url: str
    prev: str
    edges = set({})
    backlinks_from: set[str]
    html: str
    root_node: Self

    def __init__(self, prev: str, url: str, root_node: Self | None = None) -> None:
        self.url = url
        self.prev = prev
        self.edges: set[URLNode] = set({})
        self.backlinks_from = set({})
        if root_node is not None:
            self.root_node = root_node
        else:
            self.root_node = self
    
    
    def fill(self) -> None:
        self.fetch_url()
        self.get_edges()
        self.fill_edges()


    def fetch_url(self) -> None:
        res = requests.get(self.root_node.url + '/' + self.url)
        self.html = res.text


    def get_edges(self) -> None:
        soup = BeautifulSoup(self.html)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith(self.root_node.url):
                if href.startswith('/'):
                    href = '/' + href
            self.edges.add(URLNode(self.url, href, self.root_node))


    def fill_edges(self) -> None:
        for edge in self.edges:
            print(edge)
            edge.fill()


    def __str__(self) -> str:
        return self.url



class URLNodeManager:
    root: URLNode
    root_url: str
    disallowed: list[str]
    domain_name: str
    tld: str

    def __init__(self, root_url: str) -> None:
        self.root_url = root_url
        self.root = URLNode('', root_url)
        self.get_disallowed(root_url)

    def get_disallowed(self, root_url: str) -> None:
        robots_res = requests.get(root_url + '/robots.txt')
        robot_txt_parser: RobotsParser = RobotsParser(robots_res.text.splitlines())
        robot_txt_parser.parse()
        self.disallowed = robot_txt_parser.disallowed

    def clean_url(self) -> None:
        if self.root_url.endswith('/'):
            self.root_url = self.root_url[:-1]

    def fill_values(self) -> None:
        self.domain_name = urlparse(self.root_url).netloc

    def build_graph(self) -> None:
        self.clean_url()
        self.fill_values()
        self.root.fill()

    def get_all(self) -> list[URLNode]:
        return list(self.root.edges)


if __name__ == '__main__':
    mock_url = 'https://cccgoe.de'
    manager: URLNodeManager = URLNodeManager(mock_url)
    manager.build_graph()
