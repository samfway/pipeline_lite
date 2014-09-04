#!/usr/bin/env python

from __future__ import division

__author__ = "Sam Way"
__copyright__ = "Copyright 2014"
__credits__ = ["Sam Way"]
__license__ = "BSD"
__version__ = "unversioned"
__maintainer__ = "Sam Way"
__email__ = "samuel.way@colorado.edu"

from unittest import TestCase, main
from os import path

from pipeline_lite.lib.utils import get_paired_reads_from_dir
from pipeline_lite.lib.utils import parse_pipeline_config 


class TestGetPairedReads(TestCase):
    """ Test ability to find paired end reads """ 
    def setUp(self):
        self.test_dir = path.dirname(path.realpath(__file__))
        self.test_file_dir = path.join(self.test_dir, 'test_files')
        self.file_pairs = []

        for i in xrange(1, 4):
            file1 = path.join(self.test_file_dir, 'reads%d_R1_001.fastq' % i)
            file2 = path.join(self.test_file_dir, 'reads%d_R2_001.fastq' % i)
            self.file_pairs.append((file1, file2))
            

    def test(self): 
        file_pairs = get_paired_reads_from_dir(self.test_file_dir)
        file_pairs.sort()
        self.assertEqual(self.file_pairs, file_pairs)


class TestConfig(TestCase):
    """ Test parsing of configuration file """ 
    def setUp(self):
        self.test_dir = path.dirname(path.realpath(__file__))
        self.cfg_file = path.join(self.test_dir, 'test_files/test.cfg')

    def test(self):
        config = parse_pipeline_config(self.cfg_file)
        self.assertEqual(config['SPADES_EXEC'], "$HOME/tools/SPAdes-3.0.0-Linux/bin/spades.py")
        self.assertEqual(config['SEQTK_EXEC'], "seqtk")
        self.assertEqual(config['QUAST_EXEC'], "$HOME/tools/quast-2.3/metaquast.py")
        self.assertEqual(config['R1_MARKER'], "_R1_")
        self.assertEqual(config['R2_MARKER'], "_R2_")


if __name__ == '__main__':
    main()
