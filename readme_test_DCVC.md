# Testing DCVC-RT with Custom MP4 Videos

This guide explains how to test the DCVC-RT neural video codec with your own MP4 video files.

## Prerequisites

1.  **Environment**: Ensure the `DCVC` conda environment is activated.
    ```bash
    conda activate DCVC
    ```
2.  **Tools**: You need `ffmpeg` installed for video conversion.
    ```bash
    sudo apt-get install ffmpeg
    ```

## Step 1: Prepare Your Video

The test script requires raw **YUV420** format. You must convert your MP4 file first.

1.  **Check your video properties** (resolution and frame count):
    ```bash
    ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames -of default=noprint_wrappers=1 your_video.mp4
    ```

2.  **Convert MP4 to YUV**:
    ```bash
    mkdir -p media/data/my_test
    ffmpeg -y -i your_video.mp4 -c:v rawvideo -pix_fmt yuv420p media/data/my_test/your_video.yuv
    ```

## Step 2: Create Configuration File

Create a JSON config file (e.g., `dataset_config_custom.json`) to tell the script about your video.

```json
{
    "root_path": "./media/data/my_test/",
    "test_classes": {
        "MyVideo": {
            "test": 1,
            "base_path": "",
            "src_type": "yuv420",
            "sequences": {
                "your_video.yuv": {
                    "width": 1920,
                    "height": 1080,
                    "frames": 293,
                    "intra_period": -1
                }
            }
        }
    }
}
```
*   **width/height**: Must match your video exactly.
*   **frames**: The number of frames to test (can be less than total frames).
*   **intra_period**: `-1` means only the first frame is an Intra frame (standard for testing).

## Step 3: Run the Test

Run the `test_video.py` script. You can control the quality using `--qp_i` and `--qp_p` (Quantization Parameter).
*   **Higher QP (e.g., 63)** = Higher Quality / Larger Bitrate
*   **Lower QP (e.g., 22)** = Lower Quality / Smaller Bitrate

### Example: High Quality Test
```bash
python test_video.py \
    --model_path_i ./checkpoints/cvpr2025_image.pth.tar \
    --model_path_p ./checkpoints/cvpr2025_video.pth.tar \
    --rate_num 1 \
    --qp_i 63 --qp_p 63 \
    --test_config ./dataset_config_custom.json \
    --cuda 1 \
    --write_stream 1 \
    --save_decoded_frame 1 \
    --output_path output_hq.json \
    --force_intra_period -1 \
    --verbose 1
```

### Example: High Compression Test
```bash
python test_video.py \
    --model_path_i ./checkpoints/cvpr2025_image.pth.tar \
    --model_path_p ./checkpoints/cvpr2025_video.pth.tar \
    --rate_num 1 \
    --qp_i 22 --qp_p 22 \
    --test_config ./dataset_config_custom.json \
    --cuda 1 \
    --write_stream 1 \
    --save_decoded_frame 1 \
    --output_path output_lq.json \
    --force_intra_period -1 \
    --verbose 1
```

## Step 4: Visualize Results

The script outputs:
1.  **Bitstream (`.bin`)**: The compressed file (in `out_bin/MyVideo/`).
2.  **Reconstructed Video (`.yuv`)**: The decoded raw video (same size as input YUV).

To view the result, convert the reconstructed YUV back to MP4 or create a side-by-side comparison.

### Create Side-by-Side Comparison Video

Replace the filenames with your actual output paths. This example calculates the bin file size automatically and adds it to the overlay.

```bash
# 1. Set your file paths
ORIGINAL="media/data/my_test/your_video.yuv"
RECON="out_bin/MyVideo/reconstructed_video.yuv"
BIN_FILE="out_bin/MyVideo/compressed.bin"

# 2. Get the bin file size (e.g., "5.2M")
BIN_SIZE=$(du -h "$BIN_FILE" | cut -f1)

# 3. Run FFmpeg
ffmpeg -y \
    -f rawvideo -pix_fmt yuv420p -s 1920x1080 -i "$ORIGINAL" \
    -f rawvideo -pix_fmt yuv420p -s 1920x1080 -i "$RECON" \
    -filter_complex "
        [0:v]drawtext=text='Original':x=50:y=50:fontsize=48:fontcolor=white:box=1:boxcolor=black@0.5,
             pad=iw+10:ih:color=white[left];
        [1:v]drawtext=text='DCVC-RT':x=50:y=50:fontsize=48:fontcolor=white:box=1:boxcolor=black@0.5,
             drawtext=text='Bin\: $BIN_SIZE':x=50:y=110:fontsize=36:fontcolor=white:box=1:boxcolor=black@0.5[right];
        [left][right]hstack
    " \
    -c:v libx264 -crf 23 \
    output_side_by_side.mp4
```

## Understanding File Sizes

*   **`.yuv` files**: These are **uncompressed raw pixels**. They will always be huge and identical in size for the same resolution/frames, regardless of quality.
*   **`.bin` files**: These are the **actual compressed bitstreams**. Check these file sizes to see the compression performance.

# Testing DCVC-RT-Intra with Custom Images

This guide explains how to test the DCVC-RT Intra model with your own PNG images.

## Step 1: Prepare Your Images

1.  Create a folder for your images (e.g., `media/data/my_image_test`).
2.  Place your PNG images in this folder.

## Step 2: Create Configuration File

Create a JSON config file (e.g., `dataset_config_image_test.json`) to define your images.

```json
{
    "root_path": "./media/data/",
    "test_classes": {
        "MyImage": {
            "test": 1,
            "base_path": "my_image_test",
            "src_type": "png",
            "sequences": {
                "image1.png": {"width": 1920, "height": 1080, "frames": 1, "intra_period": 1},
                "image2.png": {"width": 4080, "height": 3072, "frames": 1, "intra_period": 1}
            }
        }
    }
}
```
*   **width/height**: Must match your image dimensions exactly.
*   **frames**: Set to `1` for single images.
*   **intra_period**: Set to `1`.

## Step 3: Run the Test

Use the provided `run_image_test.sh` script or run the python command directly. This script tests 3 quality levels (QP 2, 22, 63).

```bash
bash run_image_test.sh
```

Or manually:

```bash
python test_video.py \
    --model_path_i "./checkpoints/cvpr2025_image.pth.tar" \
    --model_path_p "./checkpoints/cvpr2025_video.pth.tar" \
    --rate_num 3 \
    --qp_i 2 22 63 \
    --test_config "./dataset_config_image_test.json" \
    --cuda 1 \
    --worker 1 \
    --write_stream 1 \
    --stream_path "./out_bin/image_test" \
    --save_decoded_frame 1 \
    --output_path "./test_results/output_image_test.json" \
    --force_intra True \
    --force_frame_num 1 \
    --force_intra_period 1 \
    --verbose 1
```

## Step 4: Visualize Results (Collage)

We have created a script to generate a comparison collage for each image, showing the Original vs. QP 2, QP 22, and QP 63 reconstructions along with file sizes.

1.  Ensure `create_image_collage.py` is configured with your paths (default matches the script above).
2.  Run the script:

```bash
python create_image_collage.py
```

The collages will be saved in `test_results/collages/`.
