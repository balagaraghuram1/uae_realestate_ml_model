#!/bin/bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker api_main:app --bind 0.0.0.0:$PORT
