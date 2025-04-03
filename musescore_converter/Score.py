class ScorePage:
    def __init__(self, id, page, title="", author="", composer=""):
        self.id = id
        self.page = page
        self.title = title
        self.author = author
        self.composer = composer

    def to_json(self):
        return {
            "id": self.id,
            "page": self.page,
            "title": self.title,
            "author": self.author,
            "composer": self.composer,
        }

    @staticmethod
    def get_fields():
        return ("id", "page", "title", "author", "composer")
