class Context:
    def __init__(self, domain=None, style=None, audience=None, cultural_notes=None):
        self.domain = domain
        self.style = style
        self.audience = audience
        self.cultural_notes = cultural_notes or []