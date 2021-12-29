# coding=utf-8
import json
import sys
import os
import argparse

# open config file for "RUN-COMMAND"
with open("usr/local/config/hqc_command_config.json") as json_file:
    hqc_config = json.loads(json_file.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('input_pattern',
    #             help="one input file: example.svs",
    #             nargs="*")
    
    parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(hqc_config), default="config_light", type=str)

    args = parser.parse_args()

    if args.config:
        # try to read dict from json string and update default values
        try:
            config_dict = json.loads(args.config)
            hqc_config.update(config_dict)
        except:
            print("Not a valid json config string. Using default")
    

    output_path = hqc_config["output_path"] # set output folder
    config_path = hqc_config["config_path"] # choose config file
    base_path = "-p " + hqc_config["base_path"] if len(hqc_config["base_path"]) > 1 else "" # default in qc_pipeline: "" (empty string)
    force = "-f" if json.loads(hqc_config["force"].lower()) else "" # force overwrite existing output files: default in qc_pipeline: False
    batch_size = "-b" + int(hqc_config["batch_size"]) if int(hqc_config["batch_size"]) > 0 else "" # default in config: 0 leads to default in qc_pipeline: float("inf")
    n_threads = "-n" + int(hqc_config["n_threads"]) if int(hqc_config["n_threads"]) > 1 else "" # default in qc_pipeline: 1
    symlink_off = "-s" if json.loads(hqc_config["symlink_off"].lower()) else "" # default in qc_pipeline: True

    # get filename from command line arguments:

    # create input path:
    input_path = "usr/local/data".format(folder_name)
    # create correct command to start HQC:
    command_hqc = "python usr/local/src/qc_pipeline.py {0}/*.svs -o {1} -c {2} {3} {4} {5}".format(input_path, output_path, config_path, n_threads, force, base_path)
    print(command_hqc)
    # start HQC:
    os.system(command_hqc)