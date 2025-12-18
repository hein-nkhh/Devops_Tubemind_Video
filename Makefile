.PHONY: dev-up dev-down build-all test-all

# Môi trường dev
dev-up:
	docker-compose -f docker-compose.dev.yml up -d

dev-down:
	docker-compose -f docker-compose.dev.yml down

# Build thử các service
...