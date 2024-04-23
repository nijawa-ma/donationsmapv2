#web: waitress-serve --port=$PORT donation_map.wsgi:application
#web: gunicorn donations_map:app
#web: waitress-serve --port=127.0.0.8050 donations_map:app

web: waitress-serve \
    --listen "*:$PORT" \
    --trusted-proxy '*' \
    --trusted-proxy-headers 'x-forwarded-for x-forwarded-proto x-forwarded-port' \
    --log-untrusted-proxy-headers \
    --clear-untrusted-proxy-headers \
    --threads ${WEB_CONCURRENCY:-4} \
    donations_map:wsgifunc