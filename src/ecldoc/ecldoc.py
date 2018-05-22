#!/usr/bin/env python3

import os
import glob
import argparse
import configparser

from ecldoc.Utils import joinpath, relpath, realpath
from ecldoc.Utils import split

from ecldoc.genXML import GenXML
from ecldoc.Formats.generators import generators

def configParser(configfile) :
    '''
    Parse ecldoc options from configuration file (in INI Format) and append
    them to options dictionary

    :param configfile: path to configuration file
    '''
    options = {}

    cfgparser = configparser.ConfigParser()
    cfgparser.optionxform = str
    cfgparser.read(configfile)

    options['input_root'] = None
    if 'INPUT' in cfgparser.sections() :
        options['input_root'] = realpath(cfgparser['INPUT']['root'])
        options['nodoc'] = cfgparser['INPUT'].getboolean('hideNodoc', False)
        options['nointernal'] = cfgparser['INPUT'].getboolean('hideInternal', False)

        include = ['**/*.ecl']
        if 'include' in cfgparser['INPUT'] :
            include = split(cfgparser['INPUT']['include'], sep=',')
        options['include'] = include

        exclude = []
        if 'exclude' in cfgparser['INPUT'] :
            exclude = split(cfgparser['INPUT']['exclude'], sep=',')
        options['exclude'] = exclude

    options['output_root'] = None
    options['formats'] = ['html', 'text', 'pdf']
    if 'OUTPUT' in cfgparser.sections() :
        options['output_root'] = cfgparser['OUTPUT']['root']
        if 'format' in cfgparser['OUTPUT'] :
            options['formats'] = split(cfgparser['OUTPUT']['format'], sep=',', apply=lambda x : x.lower())

    options['eclcc'] = []
    if 'ECLCC' in cfgparser.sections() :
        for key in cfgparser['ECLCC'] :
            if cfgparser['ECLCC'].getboolean(key) :
                options['eclcc'].append(key)

    options['exdoc_paths'] = []
    if 'EXDOC' in cfgparser.sections() :
        paths = split(cfgparser['EXDOC']['paths'], sep=',')
        options['exdoc_paths'] = paths

    return options

def argsParserEcldoc(args) :
    '''
    Parse command line options and return as dictionary
    :param args: command line args returned by builtin ArgumentParser
    '''
    options = {}
    if args.config is not None :
        options = configParser(args.config)
    else :
        options['input_root'] = args.iroot
        options['output_root'] = args.oroot
        options['include'] = split(args.include, ',')
        options['exclude'] = split(args.exclude, ',')
        options['eclcc'] = split(args.eclcc, ';')
        options['nodoc'] = args.hideNoDoc
        options['nointernal'] = args.hideInternal
        options['exdoc_paths'] = split(args.exdocpaths, ',', apply=lambda x : realpath(x))
        options['formats'] = split(args.format, ',', apply=lambda x : x.lower())
    return options

def doMain() :
    '''
    Main Function (Entry point for ECLDOC)
    '''
    parser = argparse.ArgumentParser(description='Parser for ECLDOC')
    parser.add_argument('--config', help="Specify configuration file")
    parser.add_argument('-i', '--iroot', help="Specify input root")
    parser.add_argument('-o', '--oroot', help="Specify output root")
    parser.add_argument('-f', '--format', help="Specify output formats separated by , (eg html,text,pdf)", default='text')
    parser.add_argument('--include', help="Specify include paths seprated by ','", default='**/*.ecl')
    parser.add_argument('--exclude', help="Specify exclude paths seprataed by ','", default='')
    parser.add_argument('--eclcc', help="Specify eclcc Options separated by ';'", default='')
    parser.add_argument('--exdocpaths', help="Specify External Documentation paths separated by ','", default='')
    parser.add_argument('--hideNoDoc', help="Hide Definitions with No Documentation", action='store_true', default=False)
    parser.add_argument('--hideInternal', help="Hide Definitions with @internal tag", action='store_true', default=False)

    args = parser.parse_args()
    print(args)

    options = argsParserEcldoc(args)
    print(options)

    if options['input_root'] is None :
        print("Input Root Not Found")
        exit(1)
    if options['output_root'] is None :
        print("Output Root Not Found")
        exit(1)

    ### Apply include and exclude glob pattern to filter files in input root source tree
    ### ecl_files : Paths to filtered files stored in ecl_files list

    ecl_files = []
    input_root = realpath(options['input_root'])
    for pattern in options['include'] :
        pattern = joinpath(input_root, pattern)
        filenames = glob.glob(pattern, recursive=True)
        filenames = [realpath(f) for f in filenames]
        ecl_files += [relpath(f, input_root) for f in filenames]

    for pattern in options['exclude'] :
        pattern = joinpath(input_root, pattern)
        filenames = glob.glob(pattern, recursive=True)
        filenames = [realpath(f) for f in filenames]
        filenames = [relpath(f, input_root) for f in filenames]
        ecl_files = list(set(ecl_files) - set(filenames))

    ### Check if output root present and create it if not

    output_root = realpath(options['output_root'])
    if not os.path.exists(output_root) :
        os.makedirs(output_root, exist_ok=True)

    ### XML Intermediate format generator
    ### ecl_file_tree : Source tree is recreated from paths in ecl_files by XML Generator
    ###                 and filtered on basis of hideInternal and hideNoDoc

    xmlgenerator = GenXML(input_root, output_root, ecl_files, options)
    xmlgenerator.run()
    ecl_file_tree = xmlgenerator.ecl_file_tree

    ### Generator is run for each format that is present in format option by user

    for f in options['formats'] :
        if f in generators :
            generators[f](input_root, output_root, ecl_file_tree, options).run()

if __name__ == "__main__" :
    doMain()