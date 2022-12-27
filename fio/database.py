import jq


class Collection():
    def __init__(self, data):
        self.data = data
    
    def find(self, query):
        return jq.compile(query).input(self.data).all()

