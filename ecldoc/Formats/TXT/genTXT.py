import os
import re

from lxml import etree
from ecldoc.Utils import write_to_file
from ecldoc.Utils import joinpath, dirname

###################################################################

from ecldoc.Constants import TEMPLATE_DIR
TXT_TEMPLATE_DIR = joinpath(TEMPLATE_DIR, 'txt')

###################################################################

import jinja2

txt_jinja_env = jinja2.Environment(
    loader = jinja2.FileSystemLoader(os.path.abspath('/'))
)

def indent_doc(s, level, width=4) :
    indention = (u' ' * (width-1) + u'| ') * level
    rv = (u'\n' + indention).join(s.splitlines())
    rv = indention + rv
    return rv

txt_jinja_env.filters['indent_doc'] = indent_doc

##################################################################

import textwrap

CPL = 100

def _break(text, CPL_E) :
    CPL_E = int(CPL_E)
    break_text = textwrap.wrap(text, CPL_E)
    if len(break_text) == 0 :
        break_text = ['']
    return break_text

##################################################################

from ecldoc.parseDoc import getTags
from ecldoc.Taglets import taglets
from .tagTXT import tag_renders

class ParseTXT(object) :
    '''
    Main class to generate TEXT Documentation for given ecl file
    from its XML Repr
    '''
    def __init__(self, generator, ecl_file) :
        self.xml_file = joinpath(generator.xml_root, ecl_file + '.xml')
        self.txt_file = joinpath(generator.txt_root, ecl_file + '.txt')
        self.template = generator.content_template
        self.options = generator.options

        os.makedirs(dirname(self.txt_file), exist_ok=True)

    def parse(self) :
        root = etree.parse(self.xml_file).getroot()
        src = root.find('Source')
        self.src = src
        self.doc = src.find('Documentation')

        for child in root.iter() :
            attribs = child.attrib
            ### Convert links from XML FOrmat to TXT Format
            if 'target' in attribs :
                attribs['target'] = re.sub(r'\$\$_ECLDOC-FORM_\$\$', 'txt', attribs['target'])
                attribs['target'] = re.sub(r'\.xml$', '.txt', attribs['target'])

        self.parseSource()

        render = self.template.render(src=src, defn_tree=self.defn_tree)
        write_to_file(self.txt_file, render)

    def docstring(self) :
        text = ''
        if self.doc is not None :
            content = self.doc.find('firstline')
            if content is not None :
                text = content.text
        return text

    def parseSource(self) :
        self.defn_tree = []
        for defn in self.src.findall('Definition') :
            self.parseDefinition(defn, self.defn_tree)

    def parseDefinition(self, defn, defn_tree) :
        headers = self.parseSign(defn)
        doc = self.parseDocs(defn)
        defn_dict = { 'headers' : headers, 'doc' : doc, 'defns' : [] }

        for childdefn in defn.findall('Definition') :
            self.parseDefinition(childdefn, defn_dict['defns'])

        defn_tree.append(defn_dict)

    def parseSign(self, defn) :
        defn_type = defn.attrib['type']
        sign = defn.find('Signature').text
        hlen = int(defn.find('Signature').attrib['hlen'])
        if defn.attrib['inherittype'] != 'local' :
            sign += ' ||| ' + defn.attrib['inherittype'].upper()

        heading = defn_type.upper() + ' : '
        spaces = len(heading)
        sign_break = _break(sign, CPL - spaces)
        type_break = [heading] + ([' '*(spaces + hlen)] * (len(sign_break) - 1))
        headers = [(a + b) for a,b in zip(type_break, sign_break)]
        return headers

    def parseDocs(self, defn) :
        renders = {}
        tags = getTags(defn.find('Documentation'))
        always = ['param', 'field', 'return', 'parent', 'content', 'firstline']
        common_tags = list(set(tags.keys()) | set(always))
        for tag in common_tags :
            if tag not in taglets or tag not in tag_renders :
                if 'generaltag' in tag_renders :
                    render = tag_renders['generaltag'](
                                taglets['generaltag'](doc=tags[tag], defn=defn, tagname=tag))
                    renders[tag] = render
                continue
            render = tag_renders[tag](taglets[tag](doc=tags[tag], defn=defn, tagname=tag))
            renders[tag] = render

        return renders

############################################################################

class GenTXT(object) :
    '''
    Generate TXT Documentation for all ecl files from XML Format
    '''
    def __init__(self, input_root, output_root, ecl_file_tree, options) :
        self.input_root = input_root
        self.output_root = output_root
        self.txt_root = joinpath(output_root, 'txt')
        self.xml_root = joinpath(output_root, 'xml')
        self.template_dir = TXT_TEMPLATE_DIR
        self.content_template = txt_jinja_env.get_template(joinpath(self.template_dir, 'content.tpl.txt'))
        self.toc_template = txt_jinja_env.get_template(joinpath(self.template_dir, 'toc.tpl.txt'))
        self.ecl_file_tree = ecl_file_tree
        self.options = options

    def gen(self, key, node, content_root) :
        '''
        Recursively parse source tree dictionary.
        If current_node is file : parse file using parseTXT
        Else If : current_node is directory : recurse and generate pkg.toc.txt for that dir
                                              (optionally generate bundle info if present)
        :param key: string | the name of current_node in path tree
        :param node: dict | the parent tree of current_node
        :param content_root: string | real path to current node in txt doc dir
        '''
        current_node = node[key]
        if type(current_node) != dict:
            if key == 'bundle.ecl' :
                return None
            parser = ParseTXT(self, current_node)
            parser.parse()
            file = { 'name' : key, 'target' : key + '.txt', 'type' : 'file', 'doc' : parser.docstring() }
            return file
        else :
            file = { 'name' : key,'target': joinpath(key, 'pkg.toc.txt'), 'type': 'dir', 'doc' : '' }

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

            childfiles = sorted(childfiles, key=lambda x : x['type'])
            os.makedirs(content_root, exist_ok=True)
            render = self.toc_template.render(name=key, files=childfiles, bundle=bundle)
            render_path = joinpath(content_root, 'pkg.toc.txt')
            write_to_file(render_path, render)

            return file

    def run(self) :
        '''
        Main function called by ecldoc
        '''
        print("\nGenerating TEXT Documentation ... ")
        self.gen('root', self.ecl_file_tree, self.txt_root)
