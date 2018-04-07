# foldershare - share folder over HTTP

This tool allows you to send all files of some folder as `.tar.gz` archive sent through HTTP server started on your local machine.

## Why

This can be useful when there is no `rsync` on other machine, or when you don't want to setup ssh access for `scp`.

So on source machine you just start `foldershare.py` in folder you want to transfer and then download all files from it as `.tar.gz` archive using `curl` or `wget` on other machine and extract files in-place:

    curl http://<source-machine>:8080/files.tar.gz | tar xz

or:

    wget http://<source-machine>:8080/files.tar.gz -O - | tar xz

## Source code

The source code is available at github: https://github.com/xHasKx/foldershare

## Pros

* Preserving files access mode and modification time
* You need only `pyhton3` on source machine, and **no additional modules**
* No need for `rsync` on target machine - it can be a simple BusyBox-like hardware
* You can specify any port and address to start HTTP server

## Cons

* Files are archived and transmitted in full every time

## Usage

Call `/path/to/foldershare.py --help` to get short usage info in your terminal.

Then on source machine:

    cd <folder-to-share>
    /path/to/foldershare.py

or

    /path/to/foldershare.py 9000 # to set alternative port 9000 for HTTP server

or

    /path/to/foldershare.py 9000 localhost # to set alternative port 9000 and address for HTTP server

This will start HTTP server on specified port (or default 8080) and all interfaces. Brief usage page will be available at http://localhost:8080/

Every time you download http://localhost:8080/files.tar.gz files in your folder will be packed and sent to you in HTTP response.
