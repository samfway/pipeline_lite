#!/usr/bin/env python

from os import listdir
from os.path import isfile
from os.path import join as path_join


def get_paired_reads_from_dir(input_dir, 
                              pe_file1_marker='_R1_', 
                              pe_file2_marker='_R2_'):
    """ Build a list of paired read files 
        
        Inputs:
        input_dir - the directory to be searched 
        pe_file1_marker - substring that marks file1 in the pair
        pe_file2_marker - substring that marks file2 in the pair

        Note: function assumes file2 will have the same name 
              as file1 with the marker switched.  That is, 
              file1.replace(pe_file1_marker, pe_file2_marker)
              should be file2. 

        Returns:
        file_pairs - a list of tuples, where each tuple is...
                     (file1, file2)
    """ 
    file_pairs = [] 

    for filename in listdir(input_dir):
        if pe_file1_marker in filename:
            file1 = path_join(input_dir, filename)
            file2 = file1.replace(pe_file1_marker, pe_file2_marker) 
            if isfile(file2):
                file_pairs.append((file1, file2))

    return file_pairs


def parse_pipeline_config(config_file):
    """ Parse pipeline configuration file 
        
        Inputs:
        config_file - filename of file to be loaded 

        Retuns:
        configuration - pipeline configuration including paths
                        to pipeline executables. 
    """
    required_fields = ['SPADES_EXEC', 'SEQTK_EXEC', 'QUAST_EXEC']
    configuration = {} 
    line_number = 0

    for line in open(config_file, 'rU'):
        line_number += 1
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        pieces = line.split('=')
        if len(pieces) < 2:
            raise ValueError("Improperly formatted configuration file. " \
                             "Error on line #%d" % line_number) 
        key = pieces[0]
        value = ''.join(pieces[1:])
        configuration[key] = value

    for field in required_fields:
        if field not in configuration:
            raise ValueError("Invalid configuration file. "\
                             "Must contain field '%s'." % field)
    
    return configuration


def get_required_fields():
    """ Get fields required by pipeline config """ 
