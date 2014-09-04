#!/usr/bin/env python

from os import listdir
from os.path import isfile, basename
from os.path import join as path_join
from numpy import ceil, log10

from pipeline_lite.lib.utils import get_paired_reads_from_dir


def build_assembly_commands(config, script, file1, file2, sub_output_dir):
    """ Basic assembly pipeline: seqtk -> spades -> quast 
        
        Inputs:
        config - pipeline configuration file
        script - filename for resulting assembly script
        file1 - paired-end file 1
        file2 - paried-end file 2
        sub_output_dir - output directory for assembly 

        Returns:
        (Nothing - writes output to 'script' file)
    """
    cmds = []
    cmds.append('#!/bin/bash\n')
    cmds.append('mkdir -p %s' % (sub_output_dir))

    cmds.append('\n# Filtering - seqtk')
    filtered_file1 = path_join(sub_output_dir, 'filtered_1.fastq')
    filtered_file2 = path_join(sub_output_dir, 'filtered_2.fastq')
    cmds.append('%s trimfq %s > %s' % (config['SEQTK_EXEC'], file1, filtered_file1))
    cmds.append('%s trimfq %s > %s' % (config['SEQTK_EXEC'], file2, filtered_file2))
    
    cmds.append('\n# Quality assessment - fastqc')
    fastqc_dir = path_join(sub_output_dir, 'fastqc_out')
    cmds.append('mkdir -p %s' % (fastqc_dir))
    cmds.append('%s %s %s -o %s' % (config['FASTQC_EXEC'], 
                                    filtered_file1,
                                    filtered_file2,
                                    fastqc_dir))

    cmds.append('\n# Assembly - SPAdes')
    spades_dir = path_join(sub_output_dir, 'spades_out')
    cmds.append('mkdir -p %s' % (spades_dir))
    cmds.append('%s -o %s --pe1-1 %s --pe1-2 %s -t %s %s' % (config['SPADES_EXEC'],
                                                             spades_dir,
                                                             filtered_file1,
                                                             filtered_file2,
                                                             config['NUM_THREADS'],
                                                             config['SPADES_FLAGS']))

    cmds.append('\n# Quality assessment - quast')
    quast_dir = path_join(sub_output_dir, 'quast_out')
    cmds.append('mkdir -p %s' % (quast_dir))
    cmds.append('%s %s -o %s -t %s' % (config['QUAST_EXEC'],
                                       path_join(spades_dir, 'contigs.fasta'),
                                       quast_dir,
                                       config['NUM_THREADS']))

    cmds.append('\n# Clean up')
    cmds.append('rm -rf %s/corrected' % (spades_dir))
    cmds.append('rm -f %s' % (filtered_file1))
    cmds.append('rm -f %s' % (filtered_file2))

    # Write to file
    output = open(script, 'w')
    output.write('\n'.join(cmds) + '\n')
    return 


def generate_launch_script(output_file, num_scripts, scripts_dir, threads, 
                           memory, log_dir, slot_limit=None):
    slot_limit_str = ''
    if slot_limit is not None and num_scripts > slot_limit:
        slot_limit_str = '%%%d' % slot_limit

    output = open(output_file, 'w')
    output.write('#!/bin/bash\n')
    output.write('#PBS -N assembly\n')
    output.write('#PBS -t 0-%d%s\n' % (num_scripts-1, slot_limit_str))
    output.write('#PBS -l nodes=1:ppn=%d\n' % (threads))
    output.write('#PBS -l pvmem=%dgb\n' % (memory))
    output.write('#PBS -o %s\n' % (path_join(log_dir, 'log')))
    output.write('#PBS -joe\n')
    output.write('#PBS -q memroute\n')
    output.write(path_join(scripts_dir, '${PBS_ARRAYID}.sh'))
    output.close()


def assemble_directory(input_dir, output_dir, scripts_dir, config):
    file1_marker = config['R1_MARKER']
    paired_reads = get_paired_reads_from_dir(input_dir)
    num_pairs = len(paired_reads)
    num_digits = int(ceil(log10(num_pairs)))  # Used to zero-pad small numbers

    for index, (file1, file2) in enumerate(paired_reads):
        prefix = str(index).zfill(num_digits)
        identifier = '%s_%s' % (prefix, basename(file1.split(file1_marker)[0]))
        script = path_join(scripts_dir, str(index)+'.sh')
        sub_output_dir = path_join(output_dir, identifier)
        build_assembly_commands(config, script, file1, file2, sub_output_dir)
                                
    launch_script = path_join(scripts_dir, 'launch.sh')
    if 'SLOT_LIMIT' in config:
        slot_limit = int(config['SLOT_LIMIT'])
    else:
        slot_limit = None

    generate_launch_script(launch_script, len(paired_reads), scripts_dir, 
                           int(config['NUM_THREADS']),
                           int(config['MEMORY_GB']),
                           output_dir,
                           slot_limit)

