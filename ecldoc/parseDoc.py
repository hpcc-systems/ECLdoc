import re
from lxml import etree
import lxml.html as H
from collections import defaultdict

def parseDocstring(docstring) :
    '''
    Parse Docstring as returned by eclcc,
    break into individual tags and
    return them as XML Elements
    '''
    docstring = re.sub(r'\n\s*\*', '\n', docstring)
    docstring = re.sub(r'\r', ' ', docstring)
    docstring = docstring.strip().split('\n')

    docdict = defaultdict(list)
    current_tag = 'content'
    current_text = ""
    for line in docstring :
        is_tag = re.search(r'^\s*@', line)
        if is_tag :
            if current_tag == 'content' :
                docdict['firstline'] = [findFirstLine(current_text)]
            docdict[current_tag].append(current_text.strip())
            line = re.split(r'\s', line.lstrip(), maxsplit=1)
            tag = line[0][1:]
            if len(line) > 1:
              text = line[1]
            else:
              text = ""
            current_tag = tag
            current_text = text + '\n'
        else :
            current_text += line + '\n'


    if current_tag == 'content' :
        docdict['firstline'] = [findFirstLine(current_text)]
    docdict[current_tag].append(current_text.strip())

    for tag in docdict :
        for i, desc in enumerate(docdict[tag]) :
            root = H.fragment_fromstring(desc, create_parent='div')
            removeWS(root)
            content = etree.Element(tag)
            content.text = etree.tostring(root)
            content.text = re.sub(r'^<div>', '', content.text)
            content.text = re.sub(r'</div>$', '', content.text)
            docdict[tag][i] = content

    return docdict

def removeWS(element) :
    '''
    Format Whitespace in HTML elements in docstring
    coming from parsed XML Output of ECL File
    '''
    if element.tag == 'pre' :
        lines = element.text.split('\n')
        element.text = lines[0]

        for line in lines[1:] :
            br = etree.Element('br')
            br.tail = line
            element.append(br)
        return

    if element.text is not None :
        element.text = re.sub(r'\s+', ' ', element.text)
    for e in element.iterchildren() :
        if e.tail :
            e.tail = re.sub(r'\s+', ' ', e.tail)

        removeWS(e)

def findFirstLine(current_text) :
    '''
    Find First line in docstring content section to be used as caption
    in TOC and Tree
    '''
    split_1 = re.split(r'\.\s|\.$', current_text.strip(), maxsplit=1)
    if len(split_1) == 2 :
        return split_1[0].strip()

    split_2 = re.split(r'\n', current_text.strip(), maxsplit=1)
    return split_2[0].strip()

##########################################################

def construct_type(ele) :
    '''
    Parse Type Tree into single string representation
    '''
    if ele is None : return ''
    if type(ele) == list : return ''

    typestring = ''
    attribs = ele.attrib
    typename = attribs['type']
    if typename == 'record' :
        if 'unnamed' in attribs :
            typestring += '{ '
            fields = []
            for field in ele.findall('Field') :
                fields.append(construct_type(field.find('./Type')) + " " + field.attrib['name'])
            typestring += ' , '.join(fields) + ' }'
        else :
            typestring += attribs['origfn'] if 'origfn' in attribs else attribs['name']
    else :
        typestring += typename.upper()
        if 'origfn' in attribs :
            typestring += ' ( ' + attribs['origfn'] + ' )'
        elif 'name' in attribs :
            typestring += ' ( ' + attribs['name'] + ' )'

    if typename == 'function' :
        typestring += ' [ '
        params = []
        for p in ele.find('Params').findall('Type') :
            params.append(construct_type(p))
        typestring += ' , '.join(params) + ' ]'

    if ele.find('./Type') is not None :
        typestring += ' ( ' + construct_type(ele.find('./Type')) + ' )'

    return typestring

##########################################################

def cleansign(text) :
    '''
    Remove irrelevant prefix and suffixes from signature
    '''
    print('cleansign in = "', text, '"')
    endpos = text.rfind(':=');
    if endpos >= 0:
      text = text[:endpos]
    text = re.sub(r'^export', '', text.strip(), flags=re.I)
    text = re.sub(r'^shared', '', text, flags=re.I)
    text = re.sub(r';$', '', text, flags=re.I)
    text = re.sub(r'\s+', ' ', text.strip())
    print('cleansign out = ', text)
    return text

def breaksign(name, text) :
    '''
    Heuristically break signature of ECL Definition
    recovered from ecl file into "return name (Paramters)"
    '''
    print('breaksign line = ', name, text)
    name = name.lower()
    string = ' ' + text.lower() + ' '
    pos = 1
    open_bracks = ['{', '(', '[']
    close_bracks = ['}', ')', ']']
    stack = []

    ret, param = '', ''
    indent_len = 0
    name_len = len(name)

    for i in range(1, len(string)) :
        c = string[i]
        if c in open_bracks :
            stack.append(c)
        elif c in close_bracks :
            if stack[-1] == open_bracks[close_bracks.index(c)] :
                stack = stack[:-1]
        else :
            if len(stack) == 0 :
                m = re.match(r'[\s\)]' + name + r'([^0-9A-Za-z_])', string[pos-1:])
                if m :
                    pos = pos - 1
                    ret = text[:pos]
                    param = text[pos + name_len:]
                    indent_len = pos + name_len
                    break

        pos += 1

    return ret.strip(), param.strip(), indent_len

##########################################################

def getTags(doc) :
    '''
    Convert XML Documentation (generated using parseDocstring)
    back to JSON (ie Python Dictionary)
    '''
    tag_dict = defaultdict(list)
    if doc is None : return tag_dict
    for child in doc.getchildren() :
        tag_dict[child.tag].append(child.text)

    return tag_dict

