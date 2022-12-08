FROM registry:2

COPY certs /etc/certs
RUN ls -l /etc/certs
# run -itd --network=host -v /etc/registry/certs:/etc/certs \
# -v /data1/var/lib/registry:/var/lib/registry \
# -e REGISTRY_HTTP_TLS_CERTIFICATE=/etc/certs/server-cert.pem \
# -e REGISTRY_HTTP_TLS_KEY=/etc/certs/server-key.pem -e REGISTRY_HTTP_ADDR=0.0.0.0:5100  \
# --name registry 
#   registry:2 
