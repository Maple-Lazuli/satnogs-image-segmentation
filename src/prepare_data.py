import json
import os
from collections import Counter
import shutil
import argparse


def get_xywh(a):
    if 'label' not in a.keys():
        label = 0
    else:
        label = a['label']
    x0 = a['x_0'] / a['shape'][1]
    x1 = a['x_1'] / a['shape'][1]
    y0 = a['y_0'] / a['shape'][0]
    y1 = a['y_1'] / a['shape'][0]

    x_center = (x0 + x1) / 2
    y_center = (y0 + y1) / 2
    width = x1 - x0
    height = y1 - y0

    return f'{label} {x_center} {y_center} {width} {height}'


def verify_dir(directory, clear=False):
    if clear and os.path.exists(directory):
        shutil.rmtree(directory)
    if not os.path.exists(directory):
        os.makedirs(directory)


def create_label(basename, file_name, save_location):
    with open(file_name, "r") as file_in:
        file = json.load(file_in)

    lines = [get_xywh(a) for a in file]
    if len(lines) > 0:
        with open(os.path.join(save_location, basename) + ".txt", "w") as file_out:
            file_out.writelines("\n".join(lines))


def main(flags):
    source_dir = flags.source_dir
    yaml_name = flags.yaml_name
    save_dir = flags.save_dir
    image_dir = os.path.join(save_dir, "images")
    label_dir = os.path.join(save_dir, "labels")

    # walk the directory and look for files
    data_files = []
    for root, dirs, files in os.walk(source_dir):
        for file in files:
            data_files.append(os.path.join(root, file))
    data_files = [d for d in data_files if d.find("annotated") == -1]
    counts = Counter([d.split('/')[-1].split(".")[0] for d in data_files])

    # verify each found file has at least two keys
    keys = []
    for key in counts.keys():
        if counts[key] == 2:
            keys.append(key)

    # prepare the directories
    verify_dir(save_dir, clear=True)
    verify_dir(image_dir)
    verify_dir(label_dir)
    for sub_dir in ['train', 'test', 'validation']:
        verify_dir(os.path.join(image_dir, sub_dir))
        verify_dir(os.path.join(label_dir, sub_dir))

    # split the data into train, validate, test
    split_factor = .65
    split_data = {'train': keys[0: int(len(keys) * split_factor)]}
    remainder = keys[int(len(keys) * split_factor):]
    split_data['validation'] = remainder[0: int(len(remainder) * split_factor)]
    split_data['test'] = remainder[int(len(remainder) * split_factor):]

    print(f"train size: {len(split_data['train'])}, validate size: {len(split_data['validation'])}, test size: {len(split_data['test'])}")
    # organize the directory structure for yolov5
    for key in split_data.keys():
        for name in split_data[key]:
            for file in data_files:
                if file.find(name) != -1:
                    if file.find("jpg") != -1:
                        shutil.copy(file, os.path.join(image_dir, key))
                    elif file.find(".json") != -1:
                        create_label(name, file_name=file, save_location=os.path.join(label_dir, key))

    # create the yaml file for yolov5
    with open(os.path.join(yaml_name), "w") as file_out:
        file_out.write(f'path: {save_dir}\n')
        file_out.write(f'train: {os.path.join(image_dir, "train")[len(save_dir) + 1:]}\n')
        file_out.write(f'val: {os.path.join(image_dir, "validation")[len(save_dir) + 1:]}\n')
        file_out.write(f'test: {os.path.join(image_dir, "test")[len(save_dir) + 1:]}\n')
        file_out.write("\n")
        file_out.write("names:\n")
        for idx, val in enumerate(["Transmission", 'ASK', "PSK", "FSK", "MFSK", "TONE"]):
            file_out.write(f'  {idx}: {val}\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--source_dir', type=str,
                        default="../data_gen",
                        help='the directory that contains the data for format')

    parser.add_argument('--save_dir', type=str,
                        default="../dataset",
                        help='the directory that contains the data for format')

    parser.add_argument('--yaml_name', type=str,
                        default="generated.yaml",
                        help='the directory that contains the data for format')

    parsed_flags, _ = parser.parse_known_args()

    main(parsed_flags)
