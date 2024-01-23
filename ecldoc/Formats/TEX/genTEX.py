import os
import re
import subprocess

from lxml import etree
from ecldoc.Utils import write_to_file
from ecldoc.Utils import joinpath, relpath, dirname

##############################################################

from ecldoc.Constants import TEMPLATE_DIR
TEX_TEMPLATE_DIR = joinpath(TEMPLATE_DIR, 'tex')

##############################################################

import jinja2
latex_jinja_env = jinja2.Environment(
    block_start_string = '\\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\\VAR{',
    variable_end_string = '}',
    comment_start_string = '\\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('/'))
)

LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash '),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)

def escape_tex(value):
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval

latex_jinja_env.filters['escape_tex'] = escape_tex

###############################################################

from ecldoc.parseDoc import getTags
from ecldoc.Taglets import taglets
from .tagTEX import tag_renders

class ParseTEX(object) :
    '''
    Main class to generate TEX & PDF Documentation for given ecl file
    from its XML Repr
    '''
    def __init__(self, generator, ecl_file) :
        self.xml_file = joinpath(generator.xml_root, ecl_file + '.xml')
        self.tex_file = joinpath(generator.tex_root, ecl_file + '.tex')

        tex_relpath = relpath(self.tex_file, generator.tex_path)
        self.dirname = dirname(tex_relpath)

        self.template = generator.content_template
        self.options = generator.options

        os.makedirs(dirname(self.tex_file), exist_ok=True)

    def parse(self) :
        root = etree.parse(self.xml_file).getroot()
        src = root.find('Source')
        self.src = src
        self.doc = src.find('Documentation')

        for child in root.iter() :
            attribs = child.attrib
            if 'target' in attribs :
                attribs['target'] = re.sub(r'\$\$_ECLDOC-FORM_\$\$', joinpath('tex', 'root'), attribs['target'])
                attribs['target'] = re.sub(r'\.xml$', '.tex', attribs['target'])

        name = src.attrib['name'].split('.')
        self.parseSource()

        render = self.template.render(name=name, src=src, defn_tree=self.defn_tree, up=('toc:'+self.dirname))
        write_to_file(self.tex_file, render)

    def docstring(self) :
        text = ''
        if self.doc is not None :
            content = self.doc.find('firstline')
            if content is not None :
                text = content.text
        return text

    def parseSource(self) :
        '''
        Append all Definitions under source tag into defn_tree
        '''
        self.defn_tree = []
        for defn in self.src.findall('Definition') :
            defn_dict = self.parseDefinition(defn)
            self.defn_tree.append(defn_dict)

    def parseDefinition(self, defn) :
        '''
        Generate Dict representation of Definition for appending into defn_tree
        '''
        sign = defn.find('Signature')
        doc = self.parseDocs(defn)

        defn_dict = { 'tag' : defn, 'sign' : sign, 'doc' : doc, 'defns' : [] }

        ### Append all Children of current Definition to defn_tree
        for childdefn in defn.findall('Definition') :
            child_dict = self.parseDefinition(childdefn)
            defn_dict['defns'].append(child_dict)

        return defn_dict

    def parseDocs(self, defn) :
        renders = {}
        tags = getTags(defn.find('Documentation'))
        always = ['param', 'field', 'return', 'parent', 'content', 'firstline']
        common_tags = list(set(tags.keys()) | set(always))
        for tag in common_tags :
            if tag not in taglets or tag not in tag_renders :
                if tag in ['content', 'firstline'] :
                    assert False, 'Taglet not found for required tags (content, firstline)'
                if 'generaltag' in tag_renders :
                    render = tag_renders['generaltag'](
                                taglets['generaltag'](doc=tags[tag], defn=defn, tagname=tag))
                    renders[tag] = render
                continue
            render = tag_renders[tag](taglets[tag](doc=tags[tag], defn=defn, tagname=tag))
            renders[tag] = render

        renders['inherit'] = tag_renders['inherit'](defn.attrib['inherittype'])

        return renders

class GenTEX(object) :
    '''
    Generate TEX & PDF Documentation for all ecl files from XML Format
    '''
    def __init__(self, input_root, output_root, ecl_file_tree, options) :
        self.input_root = input_root
        self.output_root = output_root

        self.tex_path = joinpath(output_root, 'tex')
        self.tex_root = joinpath(output_root, 'tex', 'root')
        self.xml_root = joinpath(output_root, 'xml')
        os.makedirs(self.tex_root, exist_ok=True)

        self.template_dir = TEX_TEMPLATE_DIR
        self.content_template = latex_jinja_env.get_template(joinpath(self.template_dir, 'content.tpl.tex'))
        self.toc_template = latex_jinja_env.get_template(joinpath(self.template_dir, 'toc.tpl.tex'))
        self.index_template = latex_jinja_env.get_template(joinpath(self.template_dir, 'index.tpl.tex'))

        self.ecl_file_tree = ecl_file_tree
        self.options = options

    def gen(self, key, node, content_root) :
        '''
        Recursively parse source tree dictionary.
        If current_node is file : parse file using parseTEX
        Else If : current_node is directory : recurse and generate pkg.toc.tex for that dir
                                              (optionally generate bundle info if present)
        :param key: string | the name of current_node in path tree
        :param node: dict | the parent tree of current_node
        :param content_root: string | real path to current node in tex doc dir
        '''
        current_node = node[key]
        if type(current_node) != dict:
            if key == 'bundle.ecl' :
                return
            parser = ParseTEX(self, current_node)
            parser.parse()
            file = { 'name' : key, 'type' : 'file', 'doc' : parser.docstring() }
            file['target'] = relpath(parser.tex_file, self.tex_path)
            file['label'] = parser.src.attrib['name']
            return file
        else :
            os.makedirs(content_root, exist_ok=True)
            render_path = joinpath(content_root, 'pkg.toc.tex')
            temptoc_render_path = joinpath(content_root, 'pkg.tmp.tex')
            index_render_path = joinpath(content_root, 'index.tex')

            tex_relpath = relpath(content_root, self.tex_path)
            target_relpath = relpath(render_path, self.tex_path)

            file = { 'name' : key, 'type': 'dir', 'doc' : '' , 'target' : target_relpath, 'label' : tex_relpath }

            bundle = None
            if 'bundle.ecl' in current_node :
                bundle_xml_path = joinpath(self.xml_root, dirname(current_node['bundle.ecl']), 'bundle.xml')
                bundle = etree.parse(bundle_xml_path).getroot()
                file['type'] = 'bundle'

            childfiles = []
            child_keys = sorted(current_node.keys(), key=str.lower)
            for chkey in child_keys :
                child_root = joinpath(content_root, chkey)
                child_dict = self.gen(chkey, current_node, child_root)
                if child_dict is not None : childfiles.append(child_dict)

            childfiles = sorted(childfiles, key=lambda x : x['type'], reverse=True)

            render = self.toc_template.render(name=key, files=childfiles, bundle=bundle,
                                            label=tex_relpath, up=dirname(tex_relpath))
            write_to_file(render_path, render)

            render = self.toc_template.render(name=key,
                                            files=[x for x in childfiles if x['type'] == 'file'],
                                            bundle=bundle, label=tex_relpath, up="")
            write_to_file(temptoc_render_path, render)

            start_path = relpath(temptoc_render_path, self.tex_path)
            render = self.index_template.render(root=start_path)
            write_to_file(index_render_path, render)

            subprocess.run(['pdflatex ' +
                            '-output-directory ' + relpath(content_root, self.tex_path) + ' ' +
                            relpath(index_render_path, self.tex_path)],
                            cwd=self.tex_path, shell=True)

            return file

    def run(self) :
        '''
        Main Function called by ECLDOC
        '''
        print("\nGenerating PDF Documentation ... ")
        self.gen('root', self.ecl_file_tree, self.tex_root)

        render_path = joinpath(self.tex_root, 'pkg.toc.tex')
        start_path = relpath(render_path, self.tex_path)
        render = self.index_template.render(root=start_path)
        write_to_file(joinpath(self.tex_path, 'index.tex'), render)

        subprocess.run(['pdflatex index.tex'], cwd=self.tex_path, shell=True)




