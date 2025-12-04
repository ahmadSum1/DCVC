#!/bin/bash

# Activate environment if needed (assuming user is already in the right env or knows to activate it)
# conda activate ...

# Set paths
MODEL_I="./checkpoints/cvpr2025_image.pth.tar"
MODEL_P="./checkpoints/cvpr2025_video.pth.tar" # Not used for intra-only but good to have
CONFIG="./dataset_config_image_test.json"
OUTPUT="./test_results/output_image_test$(date +%Y%m%d%H%M%S).json"
STREAM_PATH="./out_bin/image_test"


# Run test
# --force_intra True: Use only Intra model (DCVC-RT-Intra)
# --write_stream 1: Save bitstream files (.bin)
# --save_decoded_frame 1: Save reconstructed images
# --rate_num 3: Test 3 rate points (QP 2, 22, 63)
# --worker 1: Use 1 worker (sufficient for single image)
# --cuda 1: Use GPU
# --verbose 1: Print details

python test_video.py \
    --model_path_i "$MODEL_I" \
    --model_path_p "$MODEL_P" \
    --rate_num 3 \
    --qp_i 2 22 63 \
    --test_config "$CONFIG" \
    --cuda 1 \
    --worker 1 \
    --write_stream 1 \
    --stream_path "$STREAM_PATH" \
    --save_decoded_frame 1 \
    --output_path "$OUTPUT" \
    --force_intra True \
    --force_frame_num 1 \
    --force_intra_period 1 \
    --verbose 1

echo "Test finished. Results saved to $OUTPUT"
