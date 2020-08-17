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
				'resolution resolution_examples/custom_1.txt' 
				'resolution resolution_examples/custom_2.txt' 
				'resolution resolution_examples/custom_3.txt' 
				'resolution resolution_examples/custom_4.txt' 
				'resolution resolution_examples/custom_5.txt' 
				'resolution resolution_examples/custom_6.txt' 
				'resolution resolution_examples/custom_7.txt' 
				'resolution resolution_examples/custom_8.txt' 
				'resolution resolution_examples/custom_9.txt' 
				'resolution resolution_examples/custom_10.txt' 
				'resolution resolution_examples/custom_11.txt' 
				'resolution resolution_examples/ai.txt' 
				'resolution resolution_examples/chicken_alfredo.txt' 
				'resolution resolution_examples/chicken_alfredo_nomilk.txt' 
				'resolution resolution_examples/chicken_broccoli_alfredo_big.txt' 
				'resolution resolution_examples/coffee.txt' 
				'resolution resolution_examples/coffee_noheater.txt' 
				'resolution resolution_examples/small_example.txt' 
				'resolution resolution_examples/small_example_2.txt' 
				'resolution resolution_examples/small_example_3.txt'
				'resolution resolution_examples/small_example_4.txt'
				'resolution resolution_examples/coffe_or_tea.txt'
				'resolution resolution_examples/coffe_or_tea_nopowder.txt'
				'cooking_test cooking_examples/chicken_alfredo.txt cooking_examples/chicken_alfredo_input.txt'
				'cooking_test cooking_examples/chicken_alfredo_nomilk.txt cooking_examples/chicken_alfredo_nomilk_input.txt'
				'cooking_test cooking_examples/chicken_broccoli_alfredo_big.txt cooking_examples/chicken_broccoli_alfredo_big_input.txt'
				'cooking_test cooking_examples/coffee.txt cooking_examples/coffee_input.txt'
				)
expectedOutput=(
				'./resolution_examples/output/custom_1.txt'
				'./resolution_examples/output/custom_2.txt'
				'./resolution_examples/output/custom_3.txt'
				'./resolution_examples/output/custom_4.txt'
				'./resolution_examples/output/custom_5.txt'
				'./resolution_examples/output/custom_6.txt'
				'./resolution_examples/output/custom_7.txt'
				'./resolution_examples/output/custom_8.txt'
				'./resolution_examples/output/custom_9.txt'
				'./resolution_examples/output/custom_10.txt'
				'./resolution_examples/output/custom_11.txt'
				'./resolution_examples/output/ai.txt'
				'./resolution_examples/output/chicken_alfredo.txt'
				'./resolution_examples/output/chicken_alfredo_nomilk.txt'
				'./resolution_examples/output/chicken_broccoli_alfredo_big.txt'
				'./resolution_examples/output/coffee.txt'
				'./resolution_examples/output/coffee_noheater.txt'
				'./resolution_examples/output/small_example.txt'
				'./resolution_examples/output/small_example_2.txt'
				'./resolution_examples/output/small_example_3.txt'
				'./resolution_examples/output/small_example_4.txt'
				'./resolution_examples/output/coffe_or_tea.txt'
				'./resolution_examples/output/coffe_or_tea_nopowder.txt'
				'./cooking_examples/output/chicken_alfredo.txt'
				'./cooking_examples/output/chicken_alfredo_nomilk.txt'
				'./cooking_examples/output/chicken_broccoli_alfredo_big.txt'
				'./cooking_examples/output/coffee.txt'
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



