from mcp.server.fastmcp import FastMCP
from ploomber_cloud.api import PloomberCloudClient
import json

mcp = FastMCP("Ploomber MCP")

client = PloomberCloudClient()

@mcp.tool()
def get_me():
    return client.me()

@mcp.tool()
def get_projects():
    return client.get_projects()

@mcp.tool()
def get_project_details(project_id: str):
    return client.get_project_by_id(project_id)

@mcp.tool()
def start_job(job_id: str):
    return client.start_job(job_id)

@mcp.tool()
def stop_job(job_id: str):
    return client.stop_job(job_id)

@mcp.tool()
def create_project(project_type: str):
    return client.create(project_type)

@mcp.tool()
def deploy_project(
    full_path_to_zip: str, 
    project_type: str, 
    project_id: str,
    secrets: dict = None,
    resources: dict = None,
    labels: list = None,
):
    if labels:
        labels = json.dumps(labels)

    return client.deploy(full_path_to_zip, project_type, project_id, secrets=secrets, resources=resources, labels=labels)

@mcp.tool()
def delete_project(project_id: str):
    return client.delete(project_id)

@mcp.tool()
def get_job_details(job_id: str):
    return client.get_job_by_id(job_id)

@mcp.tool()
def get_job_logs(job_id: str):
    return client.get_job_logs_by_id(job_id)


if __name__ == "__main__":
    mcp.run()