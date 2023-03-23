start=`date +%s`
wget -m http://www.redbull.com
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.