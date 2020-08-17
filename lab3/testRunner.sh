#!/bin/bash

IFS=""

javaCommand="java -cp ./target/classes ui.Solution "
pythonCommand="python solution.py "
cppCommand="make && ./solution resolution resolution_examples/small_example.txt "


if [ $1 == 'java' ]
then
	executingCommand=$javaCommand
elif [ $1 == 'python' ]
then
	executingCommand=$pythonCommand
elif [ $1 == 'cpp' ]
then
	executingCommand=$cppCommand
else
	echo krivi argument:[java/python/cpp]
	exit
fi


tasksToExecute=(
				'datasets/volleyball.csv datasets/volleyball_test.csv config/id3.cfg'
				'datasets/volleyball.csv datasets/volleyball_test.csv config/id3_maxd1.cfg'
				'datasets/logic_small.csv datasets/logic_small_test.csv config/id3.cfg'
				'datasets/logic_small.csv datasets/logic_small_test.csv config/id3_maxd1.cfg'
				'datasets/titanic_train_categorical.csv datasets/titanic_test_categorical.csv config/id3.cfg'
				'datasets/titanic_train_categorical.csv datasets/titanic_test_categorical.csv config/id3_maxd1.cfg'
				)
expectedOutput=(
				'./output/volleyball_id3.txt'
				'./output/volleyball_id3_maxd1.txt'
				'./output/logic_small_id3.txt'
				'./output/logic_small_id3_maxd1.txt'
				'./output/titanic_id3.txt'
				'./output/titanic_id3_maxd1.txt'
				)
tempOutput='temp_output.txt'

i=0
failed=0
ok=0;

for taskToExecute in ${tasksToExecute[*]}
do
	touch $tempOutput
	line=$executingCommand$taskToExecute
	eval $line > $tempOutput
	
	if [ $(diff -w -B "$tempOutput" "${expectedOutput[$i]}") ] 
	then
		echo
		failed=$(($failed+1))
		echo $taskToExecute FAILED
		echo "expected output:"
		cat ${expectedOutput[$i]}
		echo
		echo "actually:"
		cat $tempOutput
		echo
	else
		ok=$(($ok+1))
		echo $taskToExecute ok
	fi
	
	rm $tempOutput
	i=$(($i+1))
done

echo
echo failed: $failed
echo ok:     $ok
echo
echo percentage: $(($ok*100/($ok+$failed)))%



