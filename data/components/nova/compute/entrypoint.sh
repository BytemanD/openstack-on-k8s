
PATCH_DIR=$1

if [[ ! -z "${PATCH_DIR}" ]]; then
    yum install -y patch
    for patchFile in $(ls -1 /var/log/nova/*.patch)
    do
        patch -d /usr/lib/python2.7/site-packages/ -p1 < ${patchFile}
    done
fi

su "-s", "/bin/sh" "-c" "nova-compute" "nova"
