#!/usr/bin/env python3

import os
import redis
import socket
import json

HOST = '' #Standart loopback inerface address (localhost)
PORT = 65432      # Port to listen on (non-privileged ports are > 1023)


def cached(cache, data):
    if cache.exists(data):
        return True
    else:
        cache.set(data, data)
        return False

def sendMsg(conn, message):
    conn.sendall(message.encode('utf-8'))

def sendJson(conn, data):
    conn.sendall(json.dumps(data).encode('utf-8') + '\n'.encode('utf-8'))

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    cache = redis.Redis(host='rediska', port=6379)
    cache.ping()

    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            query = json.loads(data)

            if query['action'] == 'put':
                if cached(query['key']):
                    cache.set(query['key'], query['message'])
                    sendJson(conn, {"status": "Created"})

                else:
                    sendJson(conn, {"status": "Ok"})

            elif query['action'] == 'get':
                val = cache.get(query['key'])
                if val is not None:
                     sendJson(conn, {"status": "OK", "message": value.decode('utf-8')})
                else:
                     sendJson(conn, {"status": "Not found"})

            elif query['action'] == 'delete':

                if cache.exists(query['key']):
                    cache.delete(query['key'])
                    sendJson(conn, {"status": "Ok"})

                else:
                    endJson(conn, {"status": "Not found"})

