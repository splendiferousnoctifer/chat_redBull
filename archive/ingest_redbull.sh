start=`date +%s`
wget -m --w ait=10 robots=off  http://www.redbull.com
end=`date +%s`
echo Execution time was `expr $end - $start` seconds.