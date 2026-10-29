+++
title = "Do We Trust Cloud Storage For Privacy?"
path = "/do-we-trust-cloud-storage-for-privacy/"
date = "2015-11-29T11:35:03"
include_in_feeds = true
[extra]
wordpress_id = 1164
kind = "post"
node_key = "1164"
author = "admin"
source_url = "http://zderadicka.eu/do-we-trust-cloud-storage-for-privacy/"
source_guid = "http://zderadicka.eu/?p=1164"
source_date_gmt = "2015-11-29 10:35:03"
categories = ["Admin", "Security", "Tools"]
tags = ["bash", "cloud", "encryption", "privacy"]
+++
With more generic offerings from  cloud storage providers -  up to 50GB free,   cloud storage is tempting alternative to store some of our data. I have some data, which I really do not want to loose. I already have them stored on several devices, however additional copy in cloud could help.  But how much I can trust cloud providers to keep my data private, even from their own employees.  Not that I have something super secret, but somehow I do not like idea, that some bored sysadmin, will be browsing my family photos.  Or provider  use my photos for some machine learning algorithms.

Main providers like Dropbox, Google do use some encryption, however they control  encryption keys, so they can theoretically access your data any time and in worst case provide them to third parties - like government agencies.   From what I have been looking around only few providers like <a href="https://mega.nz">Mega</a> or <a href="https://spideroak.com/">SpiderOak</a>  offer privacy  by design - which means  all encryption is done on client and they should not have any access to your keys (zero knowledge).   However how much we can trust that their implementation is flawless or that there are not intentional back-doors left? There has been some concerns about Mega security couple years ago,  but no major issues appeared since then.

So rather then trusting those guys fully, why not to take additional step and also encrypt our data, before sending them to cloud?  Additional encryption will not cost us much CPU time on current hardware (from tests - 11% of one core of old AMD CPU) and will not slow down transfers, because they are rather limited by Internet connection bandwidth.  And on Linux we have quite few quality encryption  tools like gpg or openssl, which can be relatively easily integrated into our backup/restore chains. In the rest of this article I'll describe my PoC shell script, that backs up/ restores  whole directory to MEGA, while providing additional encryption / decryption on client side.  <span id="more-1164"></span>

The script does following:


<ul>
<li>creates compressed archive of given directory ( <code>tar.gz</code>)</li>
<li>splits archive into files of a given size</li>
<li>encrypts each file with AES 256</li>
<li>Calculates SHA1 checksums for each file</li>
<li>Stores files and their checksum on MEGA</li>
</ul>


Recovery is done similarly, taking steps in reverse direction.

There is also possibility to share this backup with somebody who does not have account on MEGA.  This is possible due to unique feature of MEGA - sharing links - each file in MEGA is encrypted with unique key ( which is then encrypted with your master key).  MEGA can export links with the keys, so recipient can download and decrypt the files ( but in our case it'll be still encrypted with our additional encryption).   When backing up to MEGA with our script we can create so called manifest file, which contains links to files and also additional secret used for our private encryption.  If this file is shared somebody who has this script, he can easily download and restore the backup.

Script is designed for efficiency - processing data through piped streams, so it can handle large backups.

The script requires <a href="http://megatools.megous.com/">megatools</a> \- open source client for MEGA. And here is the script:


```sh
#!/bin/bash


BACKUP_DIR="/Root/Backup/"
PIECE_SIZE=10M
ACTION=store

trap "exit 2" SIGINT

if [[ $1 =~ -h|--help ]]; then
cat <<EOF
$0 [OPTIONS] DIRECTORY
Backups or restores directory to/from mega.co.nz.  Requires metatools to be installed.
Default action is to backup given directory.

-u|--user USER      mega user name (email)
-p|--password PWD   mega user password
-s|--secret SECRET  secret to be used for encryption/decryption of the backup
 --manifest FILE    backup manifest - can be created during   backup creation
                    manifest can be then used to download and restore backup
                    without knowing your mega login
--piece SIZE        size of backup piece (10M, 1G ... argument to split)
-r|--restore        restore backup from mega to given directory
-d|--download       download and restore directory from manifest
-h|--help           shows this help
EOF
exit 0
fi

while [[ $# > 1 ]]
do
key="$1"
case $key in
    -u|--user) # mega user
    USER="$2"
    shift 
    ;;
    -p|--password) # mega user password
    PWD="$2"
    shift 
    ;;
    -s|--secret) # encryption password
    ENC_PWD="$2"
    shift 
    ;; 
    --piece) # size of piece
    PIECE_SIZE="$2"
    shift 
    ;; 

    --manifest)  # backup manifest - cant be used to download files by anybody
    MANIFEST="$2"
    shift
    ;;
     -d|--download) # download using manifest
    ACTION=download
    ;;   
    -r|--restore) # download and restore data
    ACTION=restore
    ;;

    *)
            # unknown option
    ;;
esac
shift
done

function store {
    if [[ -n "$1" && -d "$1" ]]; then
    NAME=`basename $1`
    MEGA_PATH=$BACKUP_DIR$NAME
    

    megamkdir -u $USER -p $PWD $BACKUP_DIR 2>/dev/null
    megarm -u $USER -p $PWD $MEGA_PATH 2>/dev/null
    megamkdir -u $USER -p $PWD $MEGA_PATH

    tar -C $1  -czv . | split --filter "openssl aes-256-cbc  -e -k \"$ENC_PWD\" -md sha256 | tee >(sha1sum -b > $TMP_DIR/\$FILE.check) | cat > $TMP_DIR/\$FILE; megaput -u $USER -p $PWD --disable-previews --path $MEGA_PATH $TMP_DIR/\$FILE.check; megaput -u $USER -p $PWD --disable-previews --path $MEGA_PATH $TMP_DIR/\$FILE; rm $TMP_DIR/\$FILE; rm $TMP_DIR/\$FILE.check" -b $PIECE_SIZE - $NAME.

    if [[ -n $MANIFEST ]]; then
        echo $ENC_PWD > $MANIFEST
        megals -u $USER -p $PWD -e -n $MEGA_PATH  >> $MANIFEST
    fi
    else
    echo "Please specify directory!" >&2
    exit 1
    fi
}

function restore {
    if [[ -n "$1"  ]]; then
        NAME=`basename $1`
        MEGA_PATH=$BACKUP_DIR$NAME
        mkdir -p $1
        FILES=`megals -u $USER -p $PWD -n $MEGA_PATH  | grep -v "\.check$"`
        if [[ -z "$FILES" ]]; then
            echo "Sorry no backup find in $MEGA_PATH" >&2
            exit 2
        fi

        (for f in $FILES; do
            megaget --no-progress -u $USER -p $PWD --path $TMP_DIR/$f.check $MEGA_PATH/$f.check 
            if [[ ! -f $TMP_DIR/$f.check ]]; then
                echo "Checksum file is missing for $f" >&2
                
                exit 4
            fi
            megaget -u $USER -p $PWD --path - $MEGA_PATH/$f |  tee >(sha1sum --status -c $TMP_DIR/$f.check ; if [[ $? != 0 ]]; then echo "ERROR $?">${TMP_DIR}ERROR; fi ) | openssl aes-256-cbc  -d -k "$ENC_PWD" -md sha256 
            rm  $TMP_DIR/$f.check
            if [[ -f ${TMP_DIR}ERROR ]]; then 
                echo "Checksum error for file $f" >&2
                exit 6
            fi
        done) | tar -C $1 -xzv
    else
        echo "Please specify directory!" >&2
        exit 1
    fi
}

function download {
    if [[ -z "$MANIFEST" ]]; then 
        echo "Must provide backup manifest file" >&2
        exit 3
    fi
    if [[ -n "$1"  ]]; then
        mkdir -p $1
        {
        read ENC_PWD 
        while { read PIECE_LINK PIECE_NAME; read CHECK_LINK CHECK_NAME;  }; do
            if [[ $CHECK_NAME != *.check || $PIECE_NAME != ${CHECK_NAME%.check} || -z $CHECK_NAME ]]; then
                echo "Invalid manifest file" >&2
                exit 8
            fi
            megadl --no-progress --path $TMP_DIR/$CHECK_NAME $CHECK_LINK 
            if [[ ! -f $TMP_DIR/$CHECK_NAME ]]; then
                echo "Checksum file is missing $CHECK_NAME" >&2| tar | tar -C $1 -xzv| tar -C $1 -xzv| tar -C $1 -xzv-C $1 -xzv
                exit 4
            fi

            megadl --path - $PIECE_LINK |  tee >(sha1sum --status -c $TMP_DIR/$CHECK_NAME ; if [[ $? != 0 ]]; then echo "ERROR $?">${TMP_DIR}ERROR; fi ) | openssl aes-256-cbc  -d -k "$ENC_PWD" -md sha256 
            rm  $TMP_DIR/$CHECK_NAME
            if [[ -f ${TMP_DIR}ERROR ]]; then 
                echo "Checksum error for file $PIECE_NAME" >&2
                exit 6
            fi
            
        done | tar -C $1 -xzv
        } <$MANIFEST
    else
        echo "Please specify directory!" >&2
        exit 1
    fi

}

if [[ ( -z "$USER" || -z "$PWD" || -z "$ENC_PWD" ) &&  $ACTION != "download" ]]; then
    echo "You must provide --user --pasword and --secret" >&2
    exit 3
fi

function cleanup {
rm -rf $TMP_DIR
}

trap cleanup EXIT

TMP_DIR=`mktemp -d`

case $ACTION in
    restore)
    restore $1
    ;;
    store)
    store $1
    ;;
    download)
    download $1
    ;;
esac


```


 

Usage is pretty simple:

To backup:


```sh
megaback.sh -u your_mega_username -p your_mega_password -s secret_password directory_to_backup
```


And then to restore:


```sh
megaback.sh -u your_mega_username -p your_mega_password -s secret_password -r directory_to_recover
```


Optionally you can backup and get manifest:


```sh
megaback.sh -u your_mega_username -p your_mega_password -s secret_password --manifest backup-details.txt directory_to_backup
```


The anybody having the manifest file and this scripts can recover backup:


```sh
megaback.sh -d --manifest backup-details.txt directory_to_restore
```


I personally tested with 32GB directory, it took some time ( several hours to backup, much longer more then half day to restore, looks like download speed from MEGA in much more limited), but generally works fine.
