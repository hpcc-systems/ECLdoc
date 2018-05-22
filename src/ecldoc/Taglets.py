class tag(object) :
    def __init__(self, **kwargs) :
        self.docstrings = kwargs['doc']
        self.defn = kwargs['defn']
        self.tagname = kwargs['tagname'] if 'tagname' in kwargs else 'tag'

class tag_param(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.params = self.defn.find('Params')
        self.tuples = {'name' : 'Parameters', 'tuples' : []}
        self.create()

    def create(self) :
        broken_ = [c.split(' ', 1) for c in self.docstrings]
        broken_ = {c[0] : c[1] for c in broken_}
        params = self.params.findall('Param') if self.params is not None else []
        params = {p.attrib['name'].lower() : p for p in params}
        gen_params = {}
        for p in broken_ :
            actual = None
            if p.lower() in params :
                actual = params[p.lower()].find('Type')
                del params[p.lower()]

            gen_params[p.lower()] = [broken_[p], actual]
            self.tuples['tuples'].append((p, broken_[p], actual))

        for p in params :
            if p not in gen_params :
                self.tuples['tuples'].append((p, 'No Doc', params[p].find('Type')))

class tag_return(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.return_type = self.defn.find('Type')
        self.return_desc = self.docstrings[0] if len(self.docstrings) > 0 else ''

class tag_see(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.tuples = {'name' : 'See' , 'tuples' : []}
        for d in self.docstrings :
            self.tuples['tuples'].append((d, ))

class tag_field(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.fields = self.defn.findall('Field')
        self.tuples = {'name' : 'Fields', 'tuples' : []}
        self.create()

    def create(self) :
        broken_ = [c.split(' ', 1) for c in self.docstrings]
        broken_ = {c[0] : c[1] for c in broken_}
        fields = self.fields
        fields = {p.attrib['name'].lower() : p for p in fields}
        gen_fields = {}
        for p in broken_ :
            actual = None
            if p.lower() in fields :
                actual = fields[p.lower()].find('Type')
                del fields[p.lower()]

            gen_fields[p.lower()] = [broken_[p], actual]
            self.tuples['tuples'].append((p, broken_[p], actual))

        for p in fields :
            if p not in gen_fields :
                self.tuples['tuples'].append((p, 'No Doc', fields[p].find('Type')))

class tag_parent(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.parents = self.defn.find('Parents')
        self.tuples = {'name' : 'Parents', 'tuples' : []}
        self.create()

    def create(self) :
        parents = self.parents.findall('Parent') if self.parents is not None else []
        for p in parents :
            if 'ref' in p.attrib : self.tuples['tuples'].append((p.attrib['ref'], p.attrib['target']))

class tag_content(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.create()

    def create(self) :
        if len(self.docstrings) == 0 :
            self.text = 'No Documentation Found'
        else :
            self.text = " ".join(self.docstrings)

class tag_firstline(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.create()

    def create(self) :
        if len(self.docstrings) == 0 :
            self.text = "No Documentation Found"
        else :
            self.text = self.docstrings[0]

class tag_generaltag(tag) :
    def __init__(self, **kwargs) :
        super().__init__(**kwargs)
        self.tuples = {'tuples' : [], 'name' : self.tagname}
        for d in self.docstrings :
            self.tuples['tuples'].append((d, ))

taglets= {  'param' : tag_param,
            'field' : tag_field,
            'see' : tag_see,
            'return' : tag_return,
            'parent' : tag_parent,
            'content' : tag_content,
            'firstline' : tag_firstline,
            'generaltag' : tag_generaltag
         }