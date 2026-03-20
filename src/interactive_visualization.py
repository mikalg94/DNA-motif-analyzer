import plotly.graph_objects as go


def create_interactive_motif_plot(results, sequence_length, output_html):
    fig = go.Figure()

    y_level = 1
    for result in results:
        positions = result["positions"]
        motif = result["motif"]

        fig.add_trace(go.Scatter(
            x=positions,
            y=[y_level] * len(positions),
            mode="markers",
            name=motif,
            text=[f"Motif: {motif}<br>Position: {pos}" for pos in positions],
            hoverinfo="text"
        ))
        y_level += 1

    fig.update_layout(
        title="Interactive motif positions on DNA sequence axis",
        xaxis_title="Position in sequence",
        yaxis_title="Motif index",
        xaxis=dict(range=[0, sequence_length])
    )

    fig.write_html(output_html)