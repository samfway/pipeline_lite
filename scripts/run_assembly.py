#!/usr/bin/env python
import argparse

from pipeline_lite.lib.utils import parse_pipeline_config
from pipeline_lite.lib.assembly import assemble_directory

def interface():
    args = argparse.ArgumentParser()
    args.add_argument('-i', '--input-dir', help='Input directory', required=True)
    args.add_argument('-o', '--output-dir', help='Output directory', required=True)
    args.add_argument('-s', '--scripts-dir', help='Scripts directory', required=True)
    args.add_argument('-c', '--configuration-file', help='Pipeline configuration',
                      default='pipeline.cfg')
    args = args.parse_args()
    return args

if __name__=="__main__":
    args = interface()
    config = parse_pipeline_config(args.configuration_file)
    assemble_directory(args.input_dir, args.output_dir, args.scripts_dir, config)
