import sqlite3

import networkx as nx

from database.db import connection, cursor


def custom_pagerank(graph, alpha=0.85, max_iterations=100, tolerance=1.0e-6):
    """
    Custom implementation of the PageRank algorithm.

    Parameters:
    - graph: A NetworkX directed graph
    - alpha: Damping factor (typically 0.85)
    - max_iterations: Maximum number of iterations
    - tolerance: Convergence threshold

    Returns:
    - Dictionary mapping nodes to PageRank scores
    """
    nodes = list(graph.nodes())
    n = len(nodes)

    # If the graph is empty, return an empty dictionary
    if n == 0:
        return {}

    # Create a mapping from node names to indices
    # node_indices = {node: i for i, node in enumerate(nodes)}

    # Initialize the PageRank scores (uniform distribution)
    pr = {node: 1.0 / n for node in nodes}

    # Precompute outgoing edges for each node
    outgoing_edges = {}
    for node in nodes:
        outgoing = list(graph.successors(node))
        outgoing_edges[node] = outgoing

    # Iterative PageRank calculation
    for _ in range(max_iterations):
        next_pr = {node: (1.0 - alpha) / n for node in nodes}

        # Calculate the contribution of each node to its neighbors
        for node in nodes:
            out_neighbors = outgoing_edges[node]
            if out_neighbors:  # If the node has outgoing edges
                weight = alpha * pr[node] / len(out_neighbors)
                for neighbor in out_neighbors:
                    next_pr[neighbor] += weight
            else:  # Distribute evenly if no outgoing edges (dangling node)
                weight = alpha * pr[node] / n
                for target in nodes:
                    next_pr[target] += weight

        # Check for convergence
        diff = sum(abs(next_pr[node] - pr[node]) for node in nodes)
        pr = next_pr
        if diff < tolerance:
            break

    # Normalize scores to sum to 1
    total = sum(score**2 for score in pr.values())
    print(f"Total PageRank score: {total}")
    return {node: score / total for node, score in pr.items()}


def calculate_page_rank():
    """Calculate PageRank scores and save them to the database"""

    # Query the page relationships
    cursor.execute("SELECT parent_url, child_url FROM page_relationships")
    relationships = cursor.fetchall()

    # Get all pages (urls)
    cursor.execute("SELECT url FROM urls")
    all_pages = [row[0] for row in cursor.fetchall()]

    # Create a directed graph
    graph = nx.DiGraph()

    # Add all pages as nodes (even if they don't have relationships)
    for page in all_pages:
        graph.add_node(page)

    # Add edges to the graph
    for parent, child in relationships:
        graph.add_edge(parent, child)

    # Calculate PageRank using our custom implementation
    pagerank_scores = custom_pagerank(graph, alpha=0.85)

    # Update the database with PageRank scores
    try:
        # Clear existing page_rank table
        cursor.execute("DELETE FROM page_rank")

        # Insert new PageRank scores
        for page, score in pagerank_scores.items():
            cursor.execute(
                "INSERT INTO page_rank (url, rank) VALUES (?, ?)", (page, score)
            )

        connection.commit()
        print(f"PageRank scores calculated and saved for {len(pagerank_scores)} pages")
    except sqlite3.Error as e:
        connection.rollback()
        print(f"Database error: {e}")