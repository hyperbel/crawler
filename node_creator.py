from urllib.parse import urlparse
import requests
from robots_parser import RobotsParser
from bs4 import BeautifulSoup


class URLNodeGraph:
    root: URLNode
    root_url: str
    disallowed: list[str]
    domain_name: str
    tld: str

    def __init__(self, root_url: str) -> None:
        self.root = URLNode('', root_url, self)
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


    def build(self) -> None:
        self.clean_url()
        self.fill_values()
        self.root.fill()


class URLNode:
    url: str
    prev: str
    edges = set({})
    backlinks_from: set[str]
    html: str
    graph: URLNodeGraph

    def __init__(self, prev: str, url: str, graph: URLNodeGraph) -> None:
        self.url = url
        self.prev = prev
        self.edges: set[URLNode] = set({})
        self.backlinks_from = set({})
        self.graph = graph
    
    
    def fill(self) -> None:
        self.fetch_url()
        self.get_edges()
        self.fill_edges()


    def fetch_url(self) -> None:
        res = requests.get(self.url)
        self.html = res.text


    def get_edges(self) -> None:
        soup = BeautifulSoup(self.html)
        for a in soup.find_all('a', href=True):
            href = a['href']
            if not href.startswith(graph.root_url):
                
            if not href.startswith('/'):
                href = 
            else
                self.edges.add(URLNode(self.url, href, self.graph))


    def fill_edges(self) -> None:
        for edge in self.edges:
            edge.fill()


if __name__ == '__main__':
    mock_url = 'https://cccgoe.de/'
    graph: URLNodeGraph = URLNodeGraph(mock_url)
    graph.build()
