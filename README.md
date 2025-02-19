# Multi Modal Retrieval System

## System Overview

The Multi Modal Retrieval System is designed to search and retrieve information images matching text query using advanced machine learning techniques.

## Key Features

- Multi-modal data processing
- CLIP for embeddings and faiss for similarity search.
- Distributed computing with Dask
- Feature store integration with Feast
- RESTful API endpoints with FastAPI
- Modular pipeline architecture with Kedro

## Prerequisites
- Python 3.9+
- Docker

## Steps to run project

1. [Run pipeline](multi-modal-retrieval-pipeline)
2. [Create feature store](multi-modal-retrieval-feature-store)
3. Run [backend](multi-modal-retrieval-backend) and [frontend](multi-modal-retrieval-frontend)


## [Kedro Pipeline](multi-modal-retrieval-pipeline)
> [!IMPORTANT]
Before you run the pipeline the data to passed through should be put in the ***multi-modal-retrieval-pipeline/data/01_raw***

To the pipeline project you should the below command which will install the necessary packages and run the pipeline automatically
```bash
 cd multi-modal-retrieval-pipeline
 sh run_pipeline.sh
```

To visualise the pipeline run
```bash
kedro viz
```

To run the Kedro pipeline (interactive)
```bash
kedro run --async
```
### Dask (Optional)

Run Kedro pipeline with Dask
```bash
kedro run --runner=multi_modal_retrieval_pipeline.runner.DaskRunner
```
Monitor your Dask tasks at if you are using Dask:
http://127.0.0.1:8787/tasks

### FAISS Custom dataset (Optional)
We create a custom dataset to process faiss files. This is defined in the [catalog](multi-modal-retrieval-pipeline/conf/base/catalog.yml).
For simplicity versioning is turned off but can be turned on by setting the flag to true.
```yml
vector_store:
  type: multi_modal_retrieval_pipeline.io.faiss_dataset.FaissDataset
  filepath: data/06_models/faiss_index.idx
#  is_versioned: true
```

## [Feast Feature Store](multi-modal-retrieval-feature-store)
After running the Kedro pipeline run the following commands in order to create the store and push features.
```bash
cd multi-modal-retrieval-feature-store
sh create_store.sh
```

> [!NOTE]
You may see DeprecationWarning which are from feast internal implementation and one from  pd.read_parquet for Passing a BlockManager to DataFrame


To view the feast the store its attributes through a ui use

```bash
feast ui
```

## [FastAPI Backend](multi-modal-retrieval-backend)

To start the backend run the following. The command will install the required packages and the server.

```bash
cd multi-modal-retrieval-backend
sh run_dev.sh
```
You can access the API on this address http://0.0.0.0:8000/docs#/

## [Vue Frontend](multi-modal-retrieval-backend)

The following commands will start up a docker container running the Vue app. Both the backend and frontend should be run at the sametime.

```bash
cd multi-modal-retrieval-frontend
sh run_frontend.sh
```
You can access Vue app on  http://localhost:3000/


## Testing

Run tests using pytest:

```bash
pytest
```
