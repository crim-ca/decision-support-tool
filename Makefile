serve:
	panel serve decision-support-tool.ipynb --prefix building-dst --autoreload --log-level=debug

build-local:
	docker build -t decision-support-tool:dev .

run-local:
	docker run -p 5006:5006 -e BOKEH_ALLOW_WS_ORIGIN=127.0.0.1:5006,localhost:5006 decision-support-tool

build-release:
	docker build -t crimca/decision-support-tool:dev .

push-release:
	docker push crimca/decision-support-tool:dev

deploy-staging:
	IAC_CONFIG=../dst-iac/staging.yaml make -C ../iac-openstack iac-recreate-vm

build-deploy:
	$(MAKE) build-release
	$(MAKE) push-release
	$(MAKE) deploy-staging
