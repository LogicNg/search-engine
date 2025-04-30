import sqlite3

import matplotlib.pyplot as plt
import networkx as nx

from database.db import connection, cursor


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

    # Calculate PageRank
    pagerank_scores = nx.pagerank(graph, alpha=0.85)

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


def plot_page_graph():
    """Visualize the page relationship graph with PageRank scores"""

    # Query the page relationships
    cursor.execute("SELECT parent_url, child_url FROM page_relationships")
    relationships = cursor.fetchall()

    # Create a directed graph
    graph = nx.DiGraph()

    # Helper function to extract page name from URL
    def extract_page_name(url):
        return url.split("/")[-1] if "/" in url else url

    # Add edges to the graph with extracted page names
    for parent, child in relationships:
        graph.add_edge(extract_page_name(parent), extract_page_name(child))

    # Calculate PageRank for visualization
    pagerank_scores = nx.pagerank(graph)

    # Scale node sizes based on PageRank
    node_sizes = [20000 * score for score in pagerank_scores.values()]

    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(graph)

    # Create node labels with PageRank scores
    node_labels = {
        node: f"{node}\n({score:.4f})" for node, score in pagerank_scores.items()
    }

    # Draw the graph with custom labels
    nx.draw(
        graph,
        pos,
        labels=node_labels,  # Use our custom labels directly here
        with_labels=True,
        node_size=node_sizes,
        node_color="lightblue",
        font_size=10,
        font_weight="bold",
        arrowsize=20,
    )

    plt.title("Page Relationships Graph with PageRank Scores")
    plt.show()
