import json
import sys
import os
import argparse
import h5py
import pandas as pd
from glob import glob
import uuid
from datetime import datetime
from pathlib import Path
import shutil
import docker
import numpy as np


class Wrapper():
    """ Wrapper Class for WSI Algorithms / Projects
    """

    def __init__(self):

        self.parser = argparse.ArgumentParser(description='')
        # self.parser.add_argument('--algo_name', help="algorithm name from dockerfile entry point", default="controller", type=str)
        self.parser.add_argument('-in', '--input_folder', default='' ,help="one input folder Eg.: /usr/local/data containing subfolders: [first], [second] each containing exactly ONE .svs file with names: first.svs and second.svs respectively",type=str)

        self.default_config_path = "/usr/local/wrapper/default_command_config.json"
        self.source_path = "/usr/local/src"
        self.data_path = "/usr/local/mount"
        self.outer_config = False
        self.default_config = False
        self.finished = False
        self.start_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        self.end_time = "None"


        self.clam_p = False
        self.clam_ch = False
        self.simclr = False
        self.hqc = False
        self.hover = False

    def parse_cmd_config(self, outer_command_config=""):
        # open mounted config file or use default for "RUN-COMMAND"
        if os.path.isfile(outer_command_config):
            with open(outer_command_config) as json_file:
                cmd_config = json.loads(json_file.read())
                self.outer_config = True
        else:
            with open(self.default_config_path) as json_file:
                cmd_config = json.loads(json_file.read())
                self.default_config = True

        return cmd_config


    def get_commit(self, repo_path):

        git_folder = Path(repo_path,'.git')
        head_name = Path(git_folder, 'HEAD').read_text().split('\n')[0].split(' ')[-1]
        head_ref = Path(git_folder,head_name)
        commit = head_ref.read_text().replace('\n','')

        return commit
    def get_algo_name(self):
        """ functions checks if the default config file (self.default_config_file") exists.
        if it exists it is assumed that the script runs inside a docker container that was prepared
        for the corresponding open source project (CLAM, HistoQC, HoVerNet and SimCLR at this point)

        Returns
        -------
        string
            name of the open source project read from default config file or "controller"
        """

        if os.path.isfile(self.default_config_path):
            cmd_config = self.parse_cmd_config()
            algo_name = cmd_config["name"]
            self.algo_name = algo_name

        else:
            algo_name = "controller"

        return algo_name

    def save_config_info(self, cmd_config, start_command):
        """Saves the used config file (with updated information (UUID) for output folder)

        Parameters
        ----------
        cmd_config : dictionary
            dictionary with configurations for command line interface
        start_command : string
            string to start the open source project using the command line interface
        """

        cfg_dict = {}
        meta_cfg_dict = {}

        meta_cfg_dict["algorithm"] = self.algo_name
        meta_cfg_dict["version"] = self.get_commit(cmd_config["src_path"])
        meta_cfg_dict["wrapper_version"] = self.get_commit(cmd_config["wrapper_path"])
        meta_cfg_dict["finished"] = self.finished
        meta_cfg_dict["default_cfg"] = self.default_config
        meta_cfg_dict["outer_cfg"] = self.outer_config
        meta_cfg_dict["start_time"] = self.start_time

        if self.finished:
            meta_cfg_dict["end_time"] = self.end_time
        meta_cfg_dict["start_command"] = start_command
        directory_path = cmd_config["output_path"]
        save_config_path = cmd_config["output_path"] + "/config"
        cfg_dict["meta_info"] = meta_cfg_dict
        cfg_dict["command_cfg"] = cmd_config

        if not os.path.isdir(save_config_path):
            os.makedirs(save_config_path)
        # Define the mode (permissions)
        mode = 0o777  # Full permissions for everyone

        # Change the directory permissions recursively
        for root, dirs, files in os.walk(directory_path):
            # Change the permissions for the directory
            os.chmod(root, mode)
            # Change the permissions for all files in the directory
            for file in files:
                os.chmod(os.path.join(root, file), mode)

            # Change the permissions for all subdirectories in the directory
            for dir in dirs:
                os.chmod(os.path.join(root, dir), mode)


        json_file = save_config_path + "/start_config.json"
        if os.path.isfile(json_file):
            os.remove(json_file)

        with open(json_file, 'w') as cfg_json:
            json.dump(cfg_dict, cfg_json)

        # copy config file
        if cmd_config["config_path"] and os.path.isfile(cmd_config["config_path"]):
            shutil.copy2(cmd_config["config_path"], save_config_path)


    def _get_clam_patch_folder(self):
        """ gets path to clam patches (png files from clam heatmap output) for HoVerNet cell segmentation

        Returns
        -------
        string
            path to clam patches 
        """

        path = os.path.join(self.data_path, "results")

        patch_dir = None

        for root, dirs, files in os.walk(path):
            for subfolder in dirs:
                if subfolder == "topk_high_attention":
                    patch_dir = os.path.join(root, "topk_high_attention")
                    # patch_paths = [os.path.join(patch_dir, patch_name) for patch_name in os.listdir(patch_dir)]

        if not patch_dir:
            print("Not started with CLAM...")
            patch_dir = os.path.join(self.data_path, "data")

            print("Trying: ", patch_dir)

        return patch_dir


    def hovernet(self):
        """ creates the start command for HoVerNet using the command config file.
        Creates UUID for output folder (if not provided)
        reads command config and sassembles string
        """

        # RUN command outside container: 
        # docker run -it --gpus all --shm-size 8G -v /home/simon/philipp/one:/usr/local/mount hover-net

        outer_command_config = "/usr/local/mount/config/hover_command_config.json"
        # default_command_config = "/usr/local/wrapper/hover-net/default_command_config.json"
        cmd_config = self.parse_cmd_config(outer_command_config)

        parser = argparse.ArgumentParser(description='')
        # parser.add_argument('input_folder',
        #             help="one input folder that contains a WSI: example.svs",
        #             nargs=1)
        parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(cmd_config), type=str)
        # parser.add_argument('-ch', '--call_hovernet', help="call create_patches.py", default=False, action="store_true")
        parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

        args = parser.parse_args()

        hovernet_base_command = "python3 /usr/local/src/run_infer.py"

        if not args.uuid:
            out_id = uuid.uuid4().hex
        else:
            out_id = args.uuid

        # add UUID to output directory
        cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id
        print("Command:")
        print(cmd_config)

        gpu = " --gpu=" + cmd_config["gpu"]
        types =  " --nr_types=" + str(cmd_config["types"])
        type_info_path = " --type_info_path=" + cmd_config["config_path"]
        batch_size = " --batch_size=" + str(cmd_config["batch_size"])
        mode = " --model_mode=" + cmd_config["mode"]
        model_path = " --model_path=" + cmd_config["model_path"]
        nr_inf_workers = " --nr_inference_workers=" + str(cmd_config["nr_inf_workers"])
        nr_post_workers = " --nr_post_proc_workers=" + str(cmd_config["nr_post_workers"])
        out_dir = " --output_dir=" + cmd_config["output_path"] # set output folder with UUID
        in_dir = " --input_dir=" + cmd_config["input_path"]

        image_mode = cmd_config["image_mode"]

        if image_mode == " wsi":
            # WSI specific parameters
            save_thumb = " --save_thumb" if cmd_config["save_thumb"] else ""
            proc_mag = " --proc_mag=" + str(cmd_config["proc_mag"])
            save_mask = " --save_mask" if cmd_config["save_mask"] else ""
            cache_path = " --cache_path=" + cmd_config["cache_path"]

            mode_specifics = in_dir + out_dir + save_thumb + proc_mag + save_mask + cache_path

        if image_mode == " tile":
            # patch specific parameters
            mem_usage = " --mem_usage=" + str(cmd_config["mem_usage"])
            draw_dot = " --draw_dot" if cmd_config["draw_dot"] else ""
            save_qupath = " --save_qupath" if cmd_config["save_qupath"] else ""

            cmd_config["input_path"] = self._get_clam_patch_folder()
            in_dir = " --input_dir=" + cmd_config["input_path"]

            mode_specifics = in_dir + out_dir + mem_usage + draw_dot + save_qupath


        start_cmd = hovernet_base_command + gpu + types + type_info_path + batch_size + mode + model_path + nr_inf_workers + nr_post_workers + image_mode + mode_specifics
        
        self.run_project(start_cmd, cmd_config)

    def hqc(self):
        """ creates the start command for HistoQC function using the command config
        """
        # docker run -it -v /home/simon/philipp/one:/usr/local/mount hqc-docker

        cmd_config = self.parse_cmd_config()

        self.parser.add_argument('-c', '--config', help="json string with config parameters: \n Defaults: {0}".format(self.default_config_path), default=self.default_config_path, type=str)
        self.parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")

        args = self.parser.parse_args()

        if args.config:
            # try to read dict from json string and update default values
            try:
                config_dict = json.loads(args.config)
                cmd_config.update(config_dict)
            except:
                print("Not a valid json config string. Using default")
        
        if not args.uuid:
            out_id = uuid.uuid4().hex
        else:
            out_id = args.uuid

        cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id # set output folder in command_dict
        output_path = cmd_config["output_path"] # set output folder

        config_path = cmd_config["config_path"]

        base_path = "-p " + cmd_config["base_path"] if len(cmd_config["base_path"]) > 1 else "" # default in qc_pipeline: "" (empty string)
        force = "-f" if cmd_config["force"] else "" # force overwrite existing output files: default in qc_pipeline: False
        batch_size = "-b" + int(cmd_config["batch_size"]) if int(cmd_config["batch_size"]) > 0 else "" # default in config: 0 leads to default in qc_pipeline: float("inf")
        n_threads = "-n" + int(cmd_config["n_threads"]) if int(cmd_config["n_threads"]) > 1 else "" # default in qc_pipeline: 1
        symlink_off = "-s" if cmd_config["symlink_off"] else "" # default in qc_pipeline: True

        input_folder = cmd_config["input_path"]
        src_path = cmd_config["src_path"]
        wrapper_path = cmd_config["wrapper_path"]

        # create correct command to start HQC:
        start_cmd = "python /usr/local/src/qc_pipeline.py {0}/*.svs -o {1} -c {2} {3} {4} {5}".format(input_folder, output_path, config_path, n_threads, force, base_path)

        self.run_project(start_cmd, cmd_config)

    def _clam_create_patches(self, cmd_config):
        """ creates the start command for clam create patches function using the command config

        Parameters
        ----------
        cmd_config : dictionary
            holds the command line argument values for clam functions

        Returns
        -------
        start_cmd [string]
            start command for clam heatmap
        
        cmd_confg [dictionary]
            updated command config
        """

        input_folder = cmd_config["input_path"]

        patch_size = cmd_config["patch_size"] # set patch size (128 needed for ARA-NET / 224 needed for VGG16 feature extraction)
        seg = "--seg" if json.loads(cmd_config["seg"].lower()) else ""
        patch = "--patch" if json.loads(cmd_config["patch"].lower()) else ""
        stitch = "--stitch" if json.loads(cmd_config["stitch"].lower()) else ""
        no_auto_skip = "--no_auto_skip" if json.loads(cmd_config["no_auto_skip"].lower()) else ""
        preset = "--preset preset.csv"
        patch_level = "--patch_level {0}".format(int(cmd_config["patch_level"])) # downsample level for patch calculation
        process_list = "--process_list process_list.csv"
        output_path = cmd_config["output_path"] # set output folder

        # create correct command to create patch coordinates using CLAM:
        start_cmd = "python3 /usr/local/src/create_patches_fp.py --source {0} --save_dir {1} --patch_size {2} {3} {4} {5}".format(input_folder, output_path, patch_size, seg, patch, stitch)

        return start_cmd, cmd_config

    def _clam_extract_features(self, cmd_config, patch_run_dir):
        """creates the start command for clam extract features function using the command config

        Parameters
        ----------
        cmd_config : dictionary
            holds the command line argument values for clam functions
        patch_run_dir : string
            path to the patch directory

        Returns
        -------
        start_cmd [string]
            start command for clam heatmap
        
        cmd_confg [dictionary]
            updated command config
        """

        input_folder = cmd_config["input_path"]
        svs_files = glob(input_folder + "/*.svs")
        output_path = cmd_config["output_path"] # set output folder
        feat_dir = output_path + "/features"
        csv_path = patch_run_dir + "/process_list_autogen.csv"
        batch_size = cmd_config["batch_size"]
        data_h5_dir = patch_run_dir

        start_cmd = "CUDA_VISIBLE_DEVICES=0 python3 /usr/local/src/extract_features_fp.py --data_slide_dir {0} --csv_path {1} --feat_dir {2} --data_h5_dir {3} --batch_size={4} --slide_ext .svs".format(input_folder, csv_path, feat_dir, data_h5_dir, batch_size)

        return start_cmd, cmd_config

    def _clam_create_heatmaps(self, cmd_config):
        """creates the start command for clam create heatmaps function using the command config
        sets the configurations in the config.yaml file and saves it

        Parameters
        ----------
        cmd_config : dictionary
            holds the command line argument values for clam functions

        Returns
        -------
        start_cmd [string]
            start command for clam heatmap
        
        cmd_confg [dictionary]
            updated command config
        """

        import yaml
        # yaml_dict = yaml.safe_load(cmd_config["heatmap_config_path"])
        with open(cmd_config["heatmap_config_path"]) as yaml_file:
            yaml_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
        
        yaml_dict["exp_arguments"]["raw_save_dir"] = cmd_config["output_path"] + "/raw"
        yaml_dict["exp_arguments"]["production_save_dir"] = cmd_config["output_path"] + "/production"
        directory_path = cmd_config["output_path"]
        save_config_path = cmd_config["output_path"] + "/config"
        yaml_save_path = save_config_path + "/" + "heatmap_config.yaml"

        if not os.path.isdir(save_config_path):
            os.makedirs(save_config_path)
        # Define the mode (permissions)
        mode = 0o777  # Full permissions for everyone

        # Change the directory permissions recursively
        for root, dirs, files in os.walk(directory_path):
            # Change the permissions for the directory
            os.chmod(root, mode)
            # Change the permissions for all files in the directory
            for file in files:
                os.chmod(os.path.join(root, file), mode)

            # Change the permissions for all subdirectories in the directory
            for dir in dirs:
                os.chmod(os.path.join(root, dir), mode)


        directory_path = save_config_path
        # Define the mode (permissions)
        mode = 0o777  # Full permissions for everyone

        # Change the directory permissions recursively
        for root, dirs, files in os.walk(directory_path):
            # Change the permissions for the directory
            os.chmod(root, mode)
            # Change the permissions for all files in the directory
            for file in files:
                os.chmod(os.path.join(root, file), mode)

            # Change the permissions for all subdirectories in the directory
            for dir in dirs:
                os.chmod(os.path.join(root, dir), mode)


        with open(yaml_save_path, 'w+') as yaml_file:
            yaml.dump(yaml_dict, yaml_file)

        heatmap_config = yaml_save_path
        start_cmd = "python3 /usr/local/src/create_heatmaps.py --config {0}".format(heatmap_config)

        return start_cmd, cmd_config

    def clam(self):
        """ depending on the configuration, calls one of the functions to create the correct command line string for 
        one of the CLAM functions: (extract patches, extract features and/or create heatmap)
        """

        # RUN command outside container: (use all gpus, increased shared memory) 
        # docker run -it --gpus all --shm-size 8G -v /home/simon/philipp/one:/usr/local/mount clam-docker -ch

        self.parser.add_argument('-c', '--config', help="json string with config parameters", type=str)
        self.parser.add_argument('-cp', '--create_patches', help="call create_patches.py", default=False, action="store_true")
        self.parser.add_argument('-ef', '--extract_features', help="call extract_features.py",default=False, action="store_true")
        self.parser.add_argument('-ch', '--create_heatmaps', help="call create_heatmaps.py", default=False, action="store_true")
        self.parser.add_argument('-a', '--all', help="Call Full Pipeline: Create Patches, Extract Features and Create Heatmaps with default configuration", default=False, action="store_true")
        self.parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")
        self.parser.add_argument('--patch_run_dir', help='UUID of extract-patches run', type=str, default="")

        args = self.parser.parse_args()

        cmd_config = self.parse_cmd_config()

        if args.patch_run_dir:
            patch_run_dir = cmd_config["output_path"] + "/" + args.patch_run_dir
        
        if not args.uuid:
            out_id = uuid.uuid4().hex
        else:
            out_id = args.uuid

        cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id # set output folder in command_dict

        if args.create_patches:
            start_cmd, cmd_config = self._clam_create_patches(cmd_config)
            self.run_project(start_cmd, cmd_config)
        if args.extract_features:
            if os.path.isdir(patch_run_dir):
                start_cmd, cmd_config = self._clam_extract_features(cmd_config, patch_run_dir)
                self.run_project(start_cmd, cmd_config)
            else:
                print("Please Check Patch Directory Path: ", args.patch_run_dir)
            
        if args.create_heatmaps:
            start_cmd, cmd_config = self._clam_create_heatmaps(cmd_config)
            self.run_project(start_cmd, cmd_config)

    def simclr_func(self):
        """ generates the start command string using the provided config file.
        Generates a UUID for the output folder.
        Finally calls "run_project"
        """

        self.parser.add_argument('-u', '--uuid', help="UUID for current algorithm run", type=str, default="")
        
        cmd_config = self.parse_cmd_config()
        input_path = cmd_config["input_path"]

        args = self.parser.parse_args()
        if not args.uuid:
            out_id = uuid.uuid4().hex
        else:
            out_id = args.uuid
            
        cmd_config["output_path"] = cmd_config["output_path"] + "/" + out_id # set output folder in command_dict
        output_path = cmd_config["output_path"] # set output folder
        
        modelpath = cmd_config["model_path"]
        start_cmd = "python3 /usr/local/src/contrastive.py -pp {0} -o {1} -m {2}".format(input_path, output_path, modelpath)

        self.run_project(start_cmd, cmd_config)


    def run_project(self, start_cmd, cmd_config):
        """ uses the provided start command string (start_cmd) to start one open source project
        and saves the config files before calling the open source project.
        Parameters
        ----------
        start_cmd : string
            start command for command line interface
        cmd_config : dictionary
            config dictionary read from config file
        """

        print("CMD_CONFIG:")
        print(cmd_config)
        print("START:")
        print(start_cmd)
        self.save_config_info(cmd_config, start_cmd)
        return_code = os.system(start_cmd)

        if return_code == 0:
            self.finished = True
            self.end_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            self.save_config_info(cmd_config, start_cmd)

    def excel_file_controller(self, args):
        """ reads the provided excel file and sets flags for algorithm containers (CLAM / SimCLR)
        iterates over all files in excel file and calls the specific containers.
        Finally writes the results paths into the excel file

        Parameters
        ----------
        args : dictionary
            command line arguments
        """
        client = docker.from_env()

        with pd.ExcelWriter(args.config_file, mode='a', if_sheet_exists='replace') as xlsx:
            worksheet = pd.read_excel(xlsx, "Sheet1")
            files = worksheet.loc[:,"Dateiname(n)"].values

            self.file_num = len(worksheet)
            count = 1
            print("Files:", self.file_num)
            results = pd.DataFrame()
            for c, row in worksheet.iterrows():
                if not c == 0 and not pd.isna(row["Dateiname(n)"]):
                    paths = row["Pfad"].split(";")
                    files = row["Dateiname(n)"].split(";")
                    print("--------------------------New Case--------------------------------")
                    results_dict = {"clam_results" : list(), "simclr_results" : list()}
                    for path, file in zip(paths, files):
                        file_path = os.path.join(path,file)
                        # check if filepath is a folder, else skip
                        if not os.path.isfile(file_path):
                            print("------Skipping: {0} -----------------".format(file_path))
                            continue
                        else:
                            self.clam_p = row.loc["clam_p"]
                            self.clam_ch = row.loc["clam_ch"]
                            self.simclr = row.loc["simclr"]
                            wsi_name = file_path.split("/data/")[-1].split(".svs")[0]
                            print(wsi_name)
                            subfolder = file_path.split("/data/")[0]
                            
                            results_id_dict = self.run_containers(client, subfolder, count)
                            for key,val in results_id_dict.items():
                                if key in results_dict and type(results_dict[key]) == None:
                                    results_dict[key] = [val]
                                else:
                                    results_dict[key].append(val)
                            count += 1

                    print(results_dict)

                    res_df = pd.DataFrame([results_dict])
                    results = pd.concat([results, res_df], ignore_index=True)
                    

            worksheet = pd.concat([worksheet, results], axis=1)
            worksheet.to_excel(xlsx, "edited")

    def input_folder_controller(self, args):
        """checks the input folder path and gets WSI paths.
        IMPORTANT: assumed data structure: "input_path/WSI-X/data/wsi-x.svs"
        set CLAM, HQC, HoVerNet = TRUE depending on what containers need to be run

        Parameters
        ----------
        args : dict
            command line arguments
        """

        self.clam_ch = True
        # self.hqc = True
        # self.hover = True

        self.dirlist = []
        for root, dirs, files in os.walk(args.input_folder):
            for f in files:
                if f.endswith(".svs"):
                    self.dirlist.append(root.split('/data')[0])

        [print(d) for d in self.dirlist]

        # image_names = self.get_images(client)
        print(self.dirlist)
        self.file_num = len(self.dirlist)
        for count, subfolder in enumerate(self.dirlist):
            results_id_dict = self.run_containers(client, subfolder, count)

    def controller(self):
        """ either reads a xlsx file or reads the file stored in the input folder depending on the
        command line argument used (either "-c" with config file or "-in" with folder path)
        """

        self.parser.add_argument('-c', '--config_file', help="xlsx file path", type=str, default="")

        args = self.parser.parse_args()

        if len(args.config_file) > 0:
            self.excel_file_controller(args)

        elif len(args.input_folder) > 0:
            self.input_folder_controller()

        else:
            print("No Input Folder or CSV file...")

    def get_images(self, client):
        container_list = ["hover-docker", "clam-docker", "hqc-docker"]
        # container_list = ["hqc-docker"]

        images = client.images.list()
        tags = [i.tags for i in images]
        image_names  = [image.tags[0].split(":")[0] for image in images if len(image.tags) > 0]
        self.available = [c for c in container_list if c in image_names]
        print("Available Containers:", self.available)

        return image_names
        # self.prepare_containers(image_names)


    def run_containers(self, client, subfolder, count):

        print("Processing Folder: ", subfolder)
        mounts = ["{0}:/usr/local/mount".format(subfolder)]
        results_id_dict = {}

        # start_hqc_container = "docker run --rm -v {0}:/usr/local/mount hqc-docker".format(subfolder)
        # start_clam_container = "docker run --rm --gpus all --shm-size 8G -v {0}:/usr/local/mount clam-docker -cp".format(subfolder)
        # start_hover_container = "docker run --rm --gpus all --shm-size 32G -v {0}:/usr/local/mount hover-docker".format(subfolder)

        if self.hqc:
            print("Starting HQC: ")
            hqc_container = client.containers.run(image="hqc-docker", auto_remove=True, volumes=mounts, detach=True)
            self._print_output(hqc_container, "HQC", self.file_num, count)

        if self.clam_p:
            print("Starting CLAM [Patches]: ")
            clam_out_id = uuid.uuid4().hex
            clam_command_params = "-u {0} -cp".format(clam_out_id)
            clam_out_folder = os.path.join(subfolder, "results", clam_out_id)
            results_id_dict["clam_results"] = clam_out_folder

            clam_container = client.containers.run(image="clam-docker", command=clam_command_params, auto_remove=True, shm_size="8G", volumes=mounts, detach=True, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])])
            self._print_output(clam_container, "CLAM", self.file_num, count)
            result = clam_container.wait()

        if self.clam_ch:
            print("Starting CLAM [Heatmaps]: ")
            clam_out_id = uuid.uuid4().hex
            clam_command_params = "-u {0} -ch".format(clam_out_id)
            clam_out_folder = os.path.join(subfolder, "results", clam_out_id)
            results_id_dict["clam_results"] = clam_out_folder

            clam_container = client.containers.run(image="clam-docker", command=clam_command_params, auto_remove=True, shm_size="8G", volumes=mounts, detach=True, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])])
            self._print_output(clam_container, "CLAM", self.file_num, count)
            result = clam_container.wait()

        if self.hover:
            print("Starting HOVER: ")
            hover_container = client.containers.run(image="hover-docker", auto_remove=True, shm_size="8G", volumes=mounts, detach=True, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])])
            self._print_output(hover_container, "HOVER-NET", self.file_num, count)

        if self.simclr:
            print("Starting SIMCLR: ")
            simclr_out_id = uuid.uuid4().hex
            simclr_command_params = "-u {0}".format(simclr_out_id)
            simclr_out_folder = os.path.join(subfolder, "results", simclr_out_id)
            results_id_dict["simclr_results"] = simclr_out_folder

            simclr_container = client.containers.run(image="simclr-docker", command=simclr_command_params, auto_remove=True, shm_size="8G", volumes=mounts, detach=True, device_requests=[docker.types.DeviceRequest(count=-1, capabilities=[['gpu']])])
            self._print_output(simclr_container, "SIMCLR", self.file_num, count)
            result = simclr_container.wait()

        return results_id_dict


    def _print_output(self, container, algo_name, file_num, count):

        output = container.attach(stdout=True, stream=True, logs=True)
        for line in output:
            print(" {0} |-| File: {1} / {2} |-| {3}".format(algo_name, count, file_num, line.decode("utf-8")))


if __name__ == "__main__":
    """ main function checks if run in docker container or as controller
    and calls corresponding wrapper functions
    """

    wrapper = Wrapper()
    algo_name = wrapper.get_algo_name()

    print("Preparing {0}".format(algo_name))

    if "controller" in algo_name:
        wrapper.controller()
    elif "hqc" in algo_name:
        wrapper.hqc()
    elif "hover" in algo_name:
        wrapper.hovernet()
    elif "clam" in algo_name:
        wrapper.clam()
    elif "simclr" in algo_name:
        wrapper.simclr_func()
