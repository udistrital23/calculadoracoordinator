PACKAGE_NAME=calculadoracoordinator

build:
	docker build -t $(PACKAGE_NAME) -f Dockerfile .
run:
	docker run -it --rm -p 8000:8000 -v $(shell pwd):/app $(PACKAGE_NAME)
