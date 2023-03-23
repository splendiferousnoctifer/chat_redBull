.PHONY: start
start:
	uvicorn main:app  --port 9000 --forwarded-allow-ips=*

.PHONY: format
format:
	black .
	isort .

#--host=0.0.0.0