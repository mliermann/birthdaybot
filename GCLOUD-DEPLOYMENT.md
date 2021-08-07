# HOWTO: Deploying to GCloud

## Summary
This document describes how to deploy birthdaybot to the Google Cloud environment, specifically to Google Kubernetes 
Engine (GKE).

## Prerequisites
The following requirements must be satisfied in order to successfully deploy this application:
* the GCloud command-line SDK tools must be installed (see https://cloud.google.com/sdk/docs/install)
* you should either have an existing GCloud project that you wish to deploy the application to, or have created a 
project for this purpose. For the remainder of this document, we will refer to this project as `gcp-project`.
* you should have either an existing GCloud SQL instance in your project where birthdaybot can store its data, or
create an instance for this application. See instructions for this below. For the rest of this document, we will assume
that your Cloud SQL instance is named `gcp-cloudsql`, has a private IP that is part of your project's default VPC, and 
can be reached from your GKE cluster. We will assume that it accepts connections on host name `gcp-cloudsql` and port 3306.
* in the Cloud SQL instance above, create a database for the application, along with a DB user and password. We will
refer to these as `bbotdb`, `bbotdbuser` and `bbotdbpass` respectively.
* you should have an existing GKE cluster that can connect to your Cloud SQL instance via a private IP.

### Creating a GCloud SQL instance
 `gcloud sql instances create INSTANCE_NAME \
--cpu=NUMBER_CPUS \
--memory=MEMORY_SIZE \
--region=REGION`

See also https://cloud.google.com/sql/docs/mysql/create-instance#gcloud 

## Building your container image
From the same directory as the Dockerfile for this project, run the below command:

`gcloud builds submit --tag gcr.io/gcp-project/birthdaybot:1.0`

On future builds, update the tag accordingly (`1.1`, `1.2` etc.) - this facilitates continuous deployment of the app.

## Deploying to Google Kubernetes Engine
Use the `kubectl cluster-info` command to confirm that you can connect to your cluster.

Edit the files `birthdaybot-gke-deployment.yaml` and `birthdaybot-gke-service.yaml` as needed.

Create a namespace `birthdaybot` with `kubectl create ns birthdaybot`.

Now deploy the birthdaybot application to the newly created namespace:
`kubectl -n birthdaybot apply -f birthdaybot-gke-deployment.yaml`

Once the command completes, use the `kubectl -n birthdaybot get pods` command to verify that three application pods
have been spun up and are running stably. If pods are crashing at this point, use the `kubectl logs` command to check
if there are DB connection errors.

Once the deployment is running, apply the service deinition file with 
`kubectl -n birthdaybot apply -f birthdaybot-gke-service.yaml`.

Allow a minute or so for the load balancer to assign an external IP; then you can use
`kubectl -n birthdaybot get services` to determine the external IP that birthdaybot is running under.

### Deploying a new version
Build a new container with an incremented version tag (e.g.1.0 -> 1.1).

Edit the file `birthdaybot-gke-deployment.yaml` to use this new container image version.

Run `kubectl -n birthdaybot apply -f birthdaybot-gke-deployment.yaml` to push the new image version to GKE. As the app
is implemented as a Kubernetes deployment, rolling out a new version incurs no downtime.

### Other options for CI/CD
https://cloud.google.com/kubernetes-engine/docs/tutorials/gitops-cloud-build



