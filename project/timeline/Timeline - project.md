package json 
    dev
    dev server - runs server ts
    dev websoocket - 


concepts : 
    SIGINT	Ctrl + C (manual stop)
    SIGTERM	System shutdown / Docker / Kubernetes stop
backend 
    lib
        mongodbconnect
            single connection only
    server 
        used for go websocket server to be used 
            when request comes from /ws it redirect to websocket server 
    websocket server 
        using default server http and websocket
            while creating server 
                transports: ['websocket', 'polling'],
                    If WebSocket fails or is not supported, the system switches to HTTP polling.
                    Types of polling:
                        Short polling: client repeatedly asks server → “any update?”
                        Long polling: server holds request until data is available