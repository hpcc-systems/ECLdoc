import os
import re
import json
import subprocess
from copy import deepcopy

from lxml import etree
from lxml.builder import E

from .Utils import genPathTree
from .Utils import joinpath, relpath, dirname, realpath
from .Utils import read_file

from .parseDoc import parseDocstring, cleansign, breaksign


class ParseXML(object):
    '''
    ParseXML is main class to generate XML Documentation for a single ecl file
    '''
    def __init__(self, generator, ecl_file):
        '''
        :param generator: GenXML object creating this object
        :param ecl_file: path to ecl_file to parse
        '''
        self.input_root = generator.input_root
        self.output_root = generator.output_root
        self.ecl_file = ecl_file

        ### complete path to ecl file
        self.input_file = joinpath(self.input_root, ecl_file)

        ### Path to file where output from eclcc -M will be stored (called xmlOriginal)
        self.xml_orig_root = generator.xml_orig_root
        self.xml_orig_file = joinpath(self.xml_orig_root, ecl_file + '.xml')

        ### Path to file where processed xml from xmlOriginal will be stored
        self.xml_root = generator.xml_root
        self.xml_file = joinpath(self.xml_root, ecl_file + '.xml')
        self.xml_dir = dirname(self.xml_file)

        self.generator = generator
        self.options = generator.options

        ### Check if any definitions remaining in xml tree after processing
        self.internal = False

        #local
        self.depends = {}
        self.src = None

    def parse(self):
        '''
        Main function called by generator on this object
        Generates both XMLOriginal and processed XML Doc
        '''

        ### Run eclcc -M on input_file to generate xmlOriginal doc
        os.makedirs(dirname(self.xml_orig_file), exist_ok=True)
        eclcc_options = ' '.join(self.options['eclcc'])
        p = subprocess.call(['eclcc -M ' + eclcc_options +
                             ' -o ' + self.xml_orig_file + ' ' +
                             self.input_file], shell=True, cwd=self.input_root)
        print("ECLCC ||| File : ", self.ecl_file, " ||| Output Code : ", p)

        if p > 0 :
            print("ECLCC Error : Removing file from documentation source tree")
            self.internal = True
            return

        tree = etree.parse(self.xml_orig_file)
        root = tree.getroot()

        ### Main loop of this function
        ### Loops over all Source Tags in xmlOriginal

        for src in root.iter('Source'):
            attribs = src.attrib
            srcpath = realpath(attribs['sourcePath'])

            ### Check each Source Tag in xmlOriginal to see if it match input_file
            ### If yes, keep it, else replace that Source Tag with Depend Tag

            if os.path.exists(srcpath) and srcpath.startswith(self.input_root):
                attribs['sourcePath'] = srcpath
                src_relpath = relpath(srcpath, self.input_root)
                tgtpath = joinpath(self.xml_root, (src_relpath + '.xml'))
                tgtpath = realpath(tgtpath)
                tgtpath = relpath(tgtpath, self.xml_dir)
                attribs['target'] = tgtpath
                if src_relpath == self.ecl_file:
                    continue

            root.remove(src)
            depend = etree.Element('Depends', sourcePath=attribs['sourcePath'])

            if 'name' in attribs:
                depend.set('name', attribs['name'])

                ### Create a entry in depend dictionary for current Source
                ### Used to map Imports and other targets to correct file
                self.depends[tuple(attribs['name'].lower().split('.'))] = depend

            ### Set Target Path to processed XML for given Dependency
            ### Match its source path to current source tree and external documentation (if any)
            if 'target' in attribs:
                depend.set('target', attribs['target'])
            else:
                if 'name' in attribs:
                    matched = self.generator.matchExdoc(attribs['name'], source=attribs['sourcePath'])
                    if matched is not None:
                        depend.set('target', matched + '.xml')
                    else:
                        depend.set('target', attribs['sourcePath'])
                else:
                    depend.set('target', attribs['sourcePath'])

            root.insert(-1, depend)

        ### Only Source Tag corresponding to input_file is left and is processed
        self.src = root.find('Source')
        self.parseSource()

        ### If no definitions left, set internal to True
        if len(self.src.findall('Definition')) == 0:
            self.internal = True

        ### write processed XML to xml_file if not internal
        if self.internal is False:
            os.makedirs(dirname(self.xml_file), exist_ok=True)
            tree.write(self.xml_file, xml_declaration=True, encoding='utf-8')

    def parseSource(self):
        attribs = self.src.attrib
        srcpath = realpath(attribs['sourcePath'])
        print('parseSource srcpath = ', srcpath)
        self.text = read_file(srcpath);

        ### Append to depend dictionary entry correspong to given file
        ###        for self referential targets
        if 'name' in attribs:
            self.depends[tuple(attribs['name'].lower().split('.'))] = self.src

        for imp in self.src.iter('Import'):
            self.parseImport(imp)

        for doc in self.src.iter('Documentation'):
            self.parseDocumentation(doc)

        for defn in self.src.findall('Definition'):
            if self.checkDefinition(defn):
                self.src.remove(defn)
            else:
                self.parseDefinition(defn)

        ### Documentation for first Definition in Source become Documentation
        ###     for the source. Useful in displaying documentation in TOCs
        maindefn = self.src.find("Definition")
        if maindefn is not None and maindefn.find('Documentation') is not None:
            docstring = deepcopy(maindefn.find('Documentation'))
            self.src.append(docstring)
        else:
            self.src.append(E('Documentation', E('content', ' ')))

    def parseDefinition(self, defn):
        print('parseDefinition defn = ', defn)
        attribs = defn.attrib
        self.generateSignature(defn)

        if 'fullname' in attribs:
            fullname = attribs['fullname']
            best_depend = self.matchPath(fullname)
            if best_depend is not None and best_depend != self.src:
                attribs['target'] = best_depend.attrib['target']
        elif 'name' in attribs:
            attribs['fullname'] = 'ecldoc-' + attribs['name']

        for childdefn in defn.findall('Definition'):
            ### Do not parse children of inherited attributes, in addition to normal checks
            if attribs['inherittype'] == 'inherited' or self.checkDefinition(childdefn):
                defn.remove(childdefn)
            else:
                self.parseDefinition(childdefn)

        parents = defn.find('Parents')
        if parents is not None:
            self.parseParents(parents)

        ### Remove unnecessary attributes
        attribs.pop('body', None)
        attribs.pop('start', None)
        attribs.pop('end', None)

    def generateSignature(self, defn):
        '''
        Generate attribute signature by reading the ecl source file where
        given Definition is present.
        Signature is text between EXPORT and :=
        '''
        attribs = defn.attrib
        name = attribs['name']
        print('generateSignature name = ', name)
        is_scope = 'type' in attribs and attribs['type'] in ['module', 'interface']
        has_params = defn.find('Params') is not None

        ecl_text = self.text
        gen_sign = False

        if 'fullname' in attribs:
            gen_sign = True
            ### MORE : if definition is scope without params, do not read file for it.
            ###        Problem in fullname resolution
            if is_scope and (not has_params) :
                gen_sign = False
            else :
                ### If definition signature in external file (eg inherited attributes)
                ### based on fullname, Find that file
                best_depend = self.matchPath(attribs['fullname'])
                if best_depend is not None and best_depend != self.src:
                    print( 'generateSignature fullname = ', best_depend.attrib['sourcePath'])
                    ecl_text = read_file(best_depend.attrib['sourcePath']);

        sign = etree.Element('Signature')
        sign.text = name
        if gen_sign and ('start' in attribs) and ('body' in attribs) :
            sign.text = ecl_text[int(attribs['start'])-2:int(attribs['body'])]
            sign.text = cleansign(sign.text)

        ### break sign text into return type, name and parameter segments (Heuristic only)
        ### Indent len = strlen(ret) + strlen(name)
        ret, param, indent_len = breaksign(name, sign.text)

        sign.attrib['name'] = name
        sign.attrib['ret'] = ret
        sign.attrib['param'] = param
        sign.attrib['hlen'] = str(indent_len)
        defn.insert(-1, sign)

    def parseDocumentation(self, doc):
        content = doc.find('content')
        #print('parseDocumentation doc = ', etree.tostring(doc))
        #print('parseDocumentation content = ', etree.tostring(content))
        elements = parseDocstring(content.text)
        doc.remove(content)
        ### Append all parsed doctags from docstring as XML Tags
        for tag in elements:
          for desc in elements[tag]:
            doc.append(desc)

    def parseImport(self, imp):
        attribs = imp.attrib
        ### Match Reference of Import to correct File/Directory Path for Linking
        if 'ref' in attribs:
            attribs['target'] = self.matchReference(attribs['ref'])

        attribs.pop('body', None)
        attribs.pop('start', None)
        attribs.pop('end', None)
        attribs.pop('fullname', None)
        attribs.pop('line', None)
        attribs.pop('inherittype', None)
        if imp.find('Documentation') is not None :
            imp.remove(imp.find('Documentation'))

    def parseParents(self, parents):
        for parent in parents.findall('Parent'):
            attribs = parent.attrib
            ### Match Reference (Fullname) of parent to correct File/Directory Path for Linking
            if 'ref' in attribs:
                attribs['target'] = self.matchReference(attribs['ref'])

    def matchReference(self, refpath):
        '''
        Match reference/fullname to correct file/dir path
        '''
        target = ''
        ### First search among Dependency Files
        best_depend = self.matchPath(refpath)
        if best_depend is not None:
            target = best_depend.attrib['target']
        else:
            ### Then search in External Documentation (assumption : only directory paths left)
            matched = self.generator.matchExdoc(refpath)
            if matched is not None:
                target = matched + '.xml'
            else:
                ### Simply Convert reference to path (assumption : only directory paths left)
                refpath = refpath.split('.') + ['pkg.toc.xml']
                target = joinpath(self.xml_root, *refpath)
                target = relpath(target, self.xml_dir)
        return target

    def matchPath(self, path):
        '''
        Find best prefix match for given fullname/reference in Depend Dictionary
        '''
        path = tuple(path.lower().split('.'))
        current_prefix = ()
        for depend_path in self.depends:
            prefix = os.path.commonprefix([path, depend_path])
            if len(prefix) > len(current_prefix):
                current_prefix = prefix

        if len(current_prefix) > 0 and current_prefix in self.depends:
            return self.depends[current_prefix]

        return None

    def checkDefinition(self, defn):
        '''
        Check if definition should be expanded or removed
        True : Definition should be removed
        '''
        test_1 = 'exported' not in defn.attrib
        test_2 = self.options['nodoc'] and (defn.find('Documentation') is None)
        test_3 = (self.options['nointernal'] and
                  (defn.find('Documentation') is not None) and
                  (defn.find('Documentation').find('internal') is not None))
        return test_1 or test_2 or test_3

###########################################################################################

def parseBundle(generator, ecl_file):
    input_file = joinpath(generator.input_root, ecl_file)
    dirpath = dirname(input_file)

    dirpath_xml_orig = dirname(joinpath(generator.xml_orig_root, ecl_file))
    dirpath_xml = dirname(joinpath(generator.xml_root, ecl_file))

    bundle_orig_path = joinpath(dirpath_xml_orig, 'bundle.orig.out')
    bundle_xml_path = joinpath(dirpath_xml, 'bundle.xml')

    os.makedirs(dirpath_xml_orig, exist_ok=True)
    p = subprocess.call(['ecl-bundle info ' + dirpath + ' > ' + bundle_orig_path], shell=True)
    print("ECL-BUNDLE ||| ", "Bundle File : ", dirpath, "Output Code : ", p)

    data = read_file(bundle_orig_path).split('\n')
    data = [x.split(':', 1) for x in data]
    data = [(x[0].strip(), x[1].strip()) for x in data if len(x) == 2]
    root = etree.Element("Bundle")
    for k in data:
        node = etree.Element(k[0])
        node.text = k[1]
        root.append(node)

    os.makedirs(dirname(bundle_xml_path), exist_ok=True)
    etree.ElementTree(root).write(bundle_xml_path, pretty_print=True, xml_declaration=True, encoding='utf-8')

###########################################################################################

class GenXML(object):
    '''
    Generate XML Doc all files in ecl_files.
    Two types of XML Docs : xmlOriginal (eclcc output) and XML (after processing)
    '''
    def __init__(self, input_root, output_root, ecl_files, options):
        self.input_root = input_root
        self.output_root = output_root
        ### Recreate Source Tree as dictionary from ecl file paths
        self.ecl_file_tree = genPathTree(ecl_files)
        self.options = options

        ### Folder where xmlOriginal files are stored
        self.xml_orig_root = joinpath(output_root, 'xmlOriginal')
        os.makedirs(self.xml_orig_root, exist_ok=True)

        ### Folder where processed XML files are stored
        self.xml_root = joinpath(output_root, 'xml')
        os.makedirs(self.xml_root, exist_ok=True)

    def gen(self, key, node, xml_root, content_root):
        '''
        Recursively parse source tree dictionary.
        If current_node is file : parse file using parseXML or parseBundle
        Else If : current_node is directory : recurse and generate pkg.toc.xml for that dir
        :param key: string | the name of current_node in path tree
        :param node: dict | the parent of current_node (parent is passed so that current_node
        					can be deleted if it is internal file)
        :param content_root: string | real path to current node
        :param xml_root: lxml.Element | current node in xml repr of path tree for TOCs
        '''
        current_node = node[key]
        if type(current_node) != dict:
            if key == 'bundle.ecl':
                parseBundle(self, current_node)
                return
            ecl_file = current_node
            parser = ParseXML(self, ecl_file)
            parser.parse()
            if parser.internal:
                del node[key]
            else:
                file = etree.Element('file')
                file.attrib['name'] = key + '.xml'
                file.text = current_node
                xml_root.append(file)
        else:
            folder = etree.Element('folder')
            xml_root.append(folder)
            folder.attrib['name'] = key

            child_keys = list(current_node.keys())
            for chkey in child_keys:
                child_root = joinpath(content_root, chkey)
                self.gen(chkey, current_node, folder, child_root)

            os.makedirs(content_root, exist_ok=True)
            toc_file = joinpath(content_root, 'pkg.toc.xml')
            etree.ElementTree(folder).write(toc_file, pretty_print=True, xml_declaration=True, encoding='utf-8')
            self.genJsonTree(current_node, content_root)

    def run(self):
        '''
        Main function called by ecldoc
        '''
        print("\nGenerating XML Documentation ... ")
        self.processExternalDoc()
        root = etree.Element('Root')
        self.gen('root', self.ecl_file_tree, root, self.xml_root)

    #######################################################################
    # Generate tree for files and subfolders in each folder for given run #
    # Currently used by External Dodc matching system .                   #
    #######################################################################

    def genJsonTree(self, tree, output_path='', dump=True):
        json_output = {}
        new_tree = deepcopy(tree)
        self.processJsonTree(new_tree)
        json_output['tree'] = new_tree
        json_output['output_root'] = self.output_root
        json_output['input_root'] = self.input_root
        if output_path != '' :
        	rel_output_path = relpath(output_path, self.xml_root)
        	json_output['include_path'] = os.path.normpath(joinpath(self.input_root, rel_output_path))
        else :
        	json_output['include_path'] = self.input_root
        if dump:
            json.dump(json_output, open(joinpath(output_path, 'tree.json'), 'w'), sort_keys=True, indent=4)

        return json_output

    def processJsonTree(self, tree):
        keys = list(tree.keys())
        for key in keys:
            if type(tree[key]) == dict:
                self.processJsonTree(tree[key])
            node = tree[key]
            del tree[key]
            tree[re.sub(r'\.ecl$', '', key.lower())] = {'key': key, 'tree': node}

    ###############################################################
    # Process External Docs and provide match function for parser #
    ###############################################################

    def processExternalDoc(self):
        self.exdocs = []
        currdoc = self.genJsonTree(self.ecl_file_tree['root'], dump=False)
        self.exdocs.append(currdoc)
        for path in self.options['exdoc_paths']:
            json_file = joinpath(path, 'tree.json')
            assert os.path.isfile(json_file), ("Exdoc file does not exists : " + json_file)
            external_doc = json.load(open(json_file))
            self.exdocs.append(external_doc)

    def matchExdoc(self, fullname, source=''):
        fullname = tuple(fullname.lower().split('.'))
        matched = None
        for exdoc in self.exdocs:
            val = self.findInTree(fullname, exdoc['tree'], '')
            if val is not None:
                if source == '' or realpath(source).startswith(exdoc['input_root']):
                    matched = joinpath(exdoc['output_root'], '$$_ECLDOC-FORM_$$', val)
                    break
        return matched

    def findInTree(self, fullname, tree, child_root):
        if type(tree) == dict:
            if len(fullname) == 0: return joinpath(child_root, 'pkg.toc')
            if fullname[0] in tree:
                return self.findInTree(fullname[1:],
                                       tree[fullname[0]]['tree'],
                                       joinpath(child_root, tree[fullname[0]]['key']))
            return None

        return tree
