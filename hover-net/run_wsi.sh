python3 /usr/local/src/run_infer.py \
--gpu='0,1' \
--nr_types=6 \
--type_info_path=/usr/local/src/type_info.json \
--batch_size=64 \
--model_mode=fast \
--model_path=/usr/local/models/pannuke/hovernet_fast_pannuke_type_tf2pytorch.tar \
--nr_inference_workers=8 \
--nr_post_proc_workers=16 \
wsi \
--input_dir=/usr/local/data/ \
--output_dir=/usr/local/data/out/ \
--save_thumb \
--proc_mag=40 \
--save_mask
