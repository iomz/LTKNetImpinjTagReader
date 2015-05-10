#!/bin/bash
TRIAL=3
EVAL_HOME=`pwd`

if [ $# = 1 ]; then
    LOG="logs/$1";
    TAGS=()

    mkdir -p logs 

    if [ -e $LOG ]; then
        read -p "File $LOG exists. Do you wish to continue? [y/N]" yn
        case $yn in
            [Yy]* ) rm -f $LOG ${LOG}.tmp ${LOG}.raw;;
            * ) exit;;
        esac
    fi

    for i in $(eval echo "{1..$TRIAL}"); do
        echo "#Trial $i";
        echo "#Trial $i" >> ${LOG}.raw;
        # Run program and store result to ${LOG}.raw
        cd ../bin/Debug && /usr/bin/mono LTKNetImpinjTagReader.exe 203.178.141.51 10000 > /tmp/tags && cd $EVAL_HOME;
        # Save the raw data
        cat /tmp/tags >> ${LOG}.raw;
        # Calc summary
        counts=`cat /tmp/tags | grep -v "^PC" | wc -l`;
        TAGS=`cat /tmp/tags | egrep -v "^PC|^#" | awk -F $'\t' '{printf("%s:%s\n", $3, $1)}' | sort | uniq`;
        uniq_counts=`echo "$TAGS" | wc -l`;
        echo "#Tags Read Count: $counts";
        echo "#Unique Tags: $uniq_counts";
        echo "#Tags Read Count: $counts\n#Unique Tags: $uniq_counts\n" >> ${LOG}.raw;

        # Collect the details for each tag
        for t in ${TAGS[@]}; do
            tag=${t%%:*};
            pcbits=${t#*:};
            t_counts=`cat /tmp/tags | grep $tag | wc -l`;
            rssis=`cat /tmp/tags | grep $tag | awk -F $F $'\t' '{print $2}'`;
            t_rssi=0;
            for rssi in $rssis; do
                t_rssi=$(($t_rssi + $rssi));
            done
            t_rssi=`ruby -e "p ($t_rssi * 1.0 / $t_counts).round(2)"`;
            echo "#Tag: $t_counts $t_rssi $tag $pcbits";
            echo "$t_counts $t_rssi $tag $pcbits" >> ${LOG}.tmp; 
        done
    done
    
    echo "#Result";
    for t in ${TAGS[@]}; do
        tag=${t%%:*};
        pcbits=${t#*:};
        count_sum=`cat ${LOG}.tmp | grep $tag | awk '{s+=$1} END {print s}'`;
        count=`ruby -e "p ($count_sum * 1.0 / $TRIAL).round(2)"`;
        rssi_sum=`cat ${LOG}.tmp | grep $tag | awk '{s+=$2} END {print s}'`;
        rssi=`ruby -e "p ($rssi_sum / $TRIAL).round(2)"`;
        echo "$count $rssi $tag $pcbits";
        echo "$count $rssi $t $pcbits" >> $LOG;
    done
fi
