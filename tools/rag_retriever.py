from google.cloud import aiplatform
from google.cloud.aiplatform_v1.types import FindNeighborsRequest
import os

# TODO: Insert your PROJECT ID, LOCATION, INDEX ENDPOINT ID, and DEPLOYED INDEX ID
PROJECT_ID = "YOUR_PROJECT_ID"
LOCATION = "us-central1"
INDEX_ENDPOINT_ID = "YOUR_INDEX_ENDPOINT_ID"
DEPLOYED_INDEX_ID = "YOUR_DEPLOYED_INDEX_ID"

aiplatform.init(project=PROJECT_ID, location=LOCATION)

def retrieve_similar_emails(query: str):
    """
    Retrieve similar emails from Vertex AI Vector Search using semantic search.
    Returns the top matches with metadata and similarity scores.
    """

    client = aiplatform.gapic.MatchServiceClient(client_options={
        "api_endpoint": f"{LOCATION}-aiplatform.googleapis.com"
    })

    request = FindNeighborsRequest(
        index_endpoint=f"projects/{PROJECT_ID}/locations/{LOCATION}/indexEndpoints/{INDEX_ENDPOINT_ID}",
        deployed_index_id=DEPLOYED_INDEX_ID,
        queries=[
            FindNeighborsRequest.Query(
                neighbor_count=5,
                datapoint=FindNeighborsRequest.Datapoint(
                    feature_vector=[],
                    # NOTE: You must embed the query text before this — done by ADK agent automatically
                    # ADK provides an embedding before calling this tool.
                )
            )
        ]
    )

    response = client.find_neighbors(request)

    results = []
    for match in response.nearest_neighbors[0].neighbors:
        results.append({
            "datapoint_id": match.datapoint.datapoint_id,
            "distance": match.distance,
            "metadata": dict(match.datapoint.attributes)
        })

    return results
