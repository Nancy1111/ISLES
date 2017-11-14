"""Toolchain for ISLES segmentation training and validation."""
import argparse
import sys
import os

from create_modules_objects import create_modules_objects_from_config


def main():
    """Function that runs training of a ISLES algorithm."""
    # _______________________________________________________________________ #
    parser = argparse.ArgumentParser(description='An algorithm for '
                                     'Ischemic Stroke Segmentation Challenge')

    parser.add_argument('-config', dest='config_path', required=True,
                        help='Path to the configuration file.')
    parser.add_argument('-o', dest='exp_out', required=True,
                        help='Path where the intermediate and final '
                             'results would be stored.')
    args = parser.parse_args()

    if not os.path.exists(args.config_path):
        print "\nConfiguration file does not exist!\n"
        sys.exit(2)

    if not os.path.exists(args.exp_out):
        try:
            os.mkdir(args.exp_out)
        except:
            print "\nOutput directory cannot be created!\n"

    modules_objects = create_modules_objects_from_config(args.config_path)

    # _______________________________________________________________________ #

    # 1. Loading modules' objects
    # _______________________________________________________________________ #
    db = modules_objects['database']
    prep = modules_objects['preprocessor']
    aug = modules_objects['augmentator']
    meta = modules_objects['meta_data_extractor']
    patch_ex = modules_objects['patch_extractor']
    seg = modules_objects['segmentator']
    post = modules_objects['postprocessor']
    # _______________________________________________________________________ #
    # 2. Loading training data and creating train valid split
    # _______________________________________________________________________ #
    db.load_training_dict()
    db.train_valid_split()
    # _______________________________________________________________________ #
    # 3. Computing normalization parameters
    # _______________________________________________________________________ #
    print "\nGetting normalization parameters..."
    prep.get_normalization_parameters(db, args.exp_out, 'train')
    # _______________________________________________________________________ #
    # 4. Computing brain masks and lesion distance maps
    # _______________________________________________________________________ #
    print "\nComputing brain masks..."
    meta.compute_brain_masks(db, args.exp_out, 'train')

    # 5. Computing alignment parameters
    # _______________________________________________________________________ #
    print "\nGetting alignment parameters..."
    prep.get_alignment_parameters(db, meta, args.exp_out, 'train')
    # _______________________________________________________________________ #
    # 6. Augmentation
    # _______________________________________________________________________ #
    print "\nData alignment and augmentation..."
    aug.augment_data(db, meta, args.exp_out, prep, 'train')
    # _______________________________________________________________________ #

    # 6. Computing lesion distance maps
    # _______________________________________________________________________ #
    print "\nComputing lesion distance maps..."
    meta.compute_lesion_distance_maps(db, args.exp_out)
    # _______________________________________________________________________ #
    # 7. Segmentator training and validation on training dataset
    # _______________________________________________________________________ #
    print "\nSegmentator training and validation..."
    seg.training_and_validation(db, meta, prep, patch_ex, args.exp_out)
    # 8. Segmentator validation in terms of Dice scores on training subset
    # _______________________________________________________________________ #
    print "\nSegmentator Dice score validation..."
    seg.compute_classification_scores(db, prep, patch_ex, args.exp_out, 'train')
    # _______________________________________________________________________ #
    # 9. Determine postprocessing parameters
    # _______________________________________________________________________ #
    print "\nDetermining postprocessing parameters..."
    post.determine_parameters(db, prep)

if __name__ == '__main__':
    main()
