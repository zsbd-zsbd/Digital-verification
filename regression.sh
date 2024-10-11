make clean

make comp 

for((loop_num=0; loop_num < 1 ;loop_num++)) do

  make sim xxxx_test1 &
  make sim xxxx_test2 &
  make sim xxxx_test3 &
  make sim xxxx_test4 &
  make sim xxxx_test5 &
  wait

  make sim xxxx_test6 &
  make sim xxxx_test7 &
  make sim xxxx_test8 &
  make sim xxxx_test9 &
  make sim xxxx_test10 &
  wait
done
