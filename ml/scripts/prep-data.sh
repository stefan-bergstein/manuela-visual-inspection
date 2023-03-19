echo "Hello, prep files for Yolov5 training..."

SRCDIR=data/manuela
DATA=data/metal-nut-data/

mkdir -p $DATA
mkdir -p $DATA/test/images
mkdir -p $DATA/test/labels
mkdir -p $DATA/train/images
mkdir -p $DATA/train/labels
mkdir -p $DATA/valid/images
mkdir -p $DATA/valid/labels


cat $SRCDIR/data/train.txt | while read f
do
 echo $f
 cp $SRCDIR/$f $DATA/train/images
 TXT=$SRCDIR/`dirname $f`/`basename $f .png`.txt
 cp $TXT $DATA/train/labels

done


cat $SRCDIR/data/test.txt | while read f
do
 echo $f
 cp $SRCDIR/$f $DATA/valid/images
 TXT=$SRCDIR/`dirname $f`/`basename $f .png`.txt
 cp $TXT $DATA/valid/labels

done

cat <<EOF >> $DATA/data.yaml
train: data/metal-nut-data/train/images
val: data/metal-nut-data/valid/images
nc: 2
names: ['scratch', 'bent']
EOF