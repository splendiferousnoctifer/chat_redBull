.PHONY: start
start:
	uvicorn main:app  --host=0.0.0.0 --port 9000 --forwarded-allow-ips=*

.PHONY: format
format:
	black .
	isort .

#--host=0.0.0.0