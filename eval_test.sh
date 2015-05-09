#!/bin/bash
TRIAL=3

if [ $# = 1 ]; then
    LOG="logs/$1";
    mkdir -p logs 

    if [ -e $LOG ]; then
        read -p "File $LOG exists. Do you wish to continue? [y/N]" yn
        case $yn in
            [Yy]* ) rm -f $LOG ${LOG}.raw ${LOG}.tmp;;
            * ) exit;;
        esac
    fi

    for i in $(eval echo "{1..$TRIAL}"); do
        echo "#Trial $i";
        echo "#Trial $i" >> ${LOG}.raw;
        # Run program and store result to /tmp/tags
        cd bin/Debug && /usr/bin/mono LTKNetImpinjTagReader.exe 203.178.141.51 10000 > /tmp/tags && cd ../../;
        # Save the raw data
        cat /tmp/tags >> ${LOG}.raw;
        # Calc summary
        counts=`cat /tmp/tags | grep -v "^PC" | wc -l`;
        tags=`cat /tmp/tags | grep -v "^PC" | awk -F $'\t' '{print $3}' | sort | uniq`;
        uniq_counts=`echo "$tags" | wc -l`;
        echo "#Summary: Tags Read Count => $counts, Unique Tags => $uniq_counts";
        echo "#Summary: Tags Read Count => $counts, Unique Tags => $uniq_counts" >> ${LOG}.raw;

        # Collect the details for each tag
        for t in $tags; do
            cat /tmp/tags | grep $t > /tmp/t;
            t_counts=`cat /tmp/t | wc -l`;
            rssis=`cat /tmp/t | awk -F $F $'\t' '{print $2}'`;
            t_rssi=0;
            for rssi in $rssis; do
                t_rssi=$(($t_rssi + $rssi));
            done
            t_rssi=`ruby -e "p ($t_rssi * 1.0 / $t_counts).round(2)"`;
            echo "#Tag: $t_counts $t_rssi $t";
            echo "$t_counts $t_rssi $t" >> ${LOG}.tmp; 
        done
    done
    
    echo "#Result";
    for t in `cat ${LOG}.tmp | awk '{print $3}' | sort | uniq`; do
        count_sum=`cat ${LOG}.tmp | grep $t | awk '{s+=$1} END {print s}'`;
        count=`ruby -e "p ($count_sum * 1.0 / $TRIAL).round(2)"`;
        rssi_sum=`cat ${LOG}.tmp | grep $t | awk '{s+=$2} END {print s}'`;
        rssi=`ruby -e "p ($rssi_sum / $TRIAL).round(2)"`;
        echo "$count $rssi $t";
        echo "$count $rssi $t" >> $LOG;
    done
fi
