# cp /etc/pki/tls/openssl.cnf ./
DNS=registry.local.io

openssl genrsa -aes256 -out ca-key.pem 4096
openssl req -new -x509 -days 36500 \
    -key ca-key.pem \
    -subj "/CN=${DNS}" \
    -out ca.pem
openssl genrsa -out server-key.pem 4096

\cp /etc/pki/tls/openssl.cnf ./
printf "[SAN]\nsubjectAltName=DNS:${DNS}\n" >> openssl.cnf

openssl req -new -sha256 \
    -key server-key.pem \
    -subj "/C=CN/OU=CLOUD/O=NUDT/CN=${DNS}" \
    -reqexts SAN \
    -config openssl.cnf \
    -out server.csr

openssl x509 -req -days 36500 \
    -in server.csr \
    -out server-cert.pem \
    -CA ca.pem \
    -CAkey ca-key.pem \
    -CAcreateserial \
    -extensions SAN \
    -extfile openssl.cnf
