from mcp.server.fastmcp import FastMCP
from worklog_mcp.tools.worklog import write_worklog, read_worklog
from worklog_mcp.tools.project_doc import (
    read_project_doc,
    create_project_doc,
    analyze_gaps,
    update_project_doc,
)
from worklog_mcp.tools.notion import write_worklog_to_notion

mcp = FastMCP("worklog-mcp")

mcp.tool()(write_worklog)
mcp.tool()(read_worklog)
mcp.tool()(read_project_doc)
mcp.tool()(create_project_doc)
mcp.tool()(analyze_gaps)
mcp.tool()(update_project_doc)
mcp.tool()(write_worklog_to_notion)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
