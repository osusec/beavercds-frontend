docker run --rm --network host caddy:latest caddy reverse-proxy --from https://damctf.xyz --to http://localhost:8000 --internal-certs
