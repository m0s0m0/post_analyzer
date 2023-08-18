# Post creation and analyzing service

This repo contains the code of  asynchronous Post creationa and analyzing service Project! This project provides an example implementation of creating and analyzing posts asynchronously using the Django framework. The custom asyncronous caching decorator with custom cache key is also present in the service.


## Getting started

### Prerequisites

1. Git [Installation guidelines](https://support.atlassian.com/bitbucket-cloud/docs/install-and-set-up-git/)
2. Docker==4.11.1


### Installation And Running Locally
1. Clone the repository
```bash
git clone https://github.com/m0s0m0/post_analyzer.git
```
Enter root directory
```bash
cd post_analyzer
```
Build the image locally by make command
```bash
make build_local
```
Run the docker image
```bash
make up_local
```

## Code Quality
Python linter flake8 has been used and it checks for error while building the microservice

### Architecture and scaling



 