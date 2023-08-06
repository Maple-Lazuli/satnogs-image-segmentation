cd yolov5
python train.py --img 1500 --epochs 60 --data ../first-generation.yaml  --batch-size -1
python train.py --img 1500 --epochs 60 --data ../threshold-transmission.yaml  --batch-size -1

