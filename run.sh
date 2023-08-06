cd yolov5 || exit
python train.py --img 1500 --epochs 60 --data ../non-threshold-subsignal.yaml  --batch-size -1
python train.py --img 1500 --epochs 60 --data ../non-threshold-transmission.yaml  --batch-size -1
python train.py --img 1500 --epochs 60 --data ../threshold-subsignal.yaml  --batch-size -1
python train.py --img 1500 --epochs 60 --data ../first-generation-v2.yaml  --batch-size -1
python train.py --img 1500 --epochs 60 --data ../threshold-transmission-v2.yaml  --batch-size -1
