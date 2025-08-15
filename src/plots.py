# src/plots.py
import plotly.graph_objects as go
import numpy as np
import pandas as pd

def histogram_with_score(totals_arr, user_score: float,
                         bin_min=0, bin_max=30, bin_step=1,
                         title="Phổ điểm"):
    bins = np.arange(bin_min, bin_max + bin_step, bin_step)
    counts, edges = np.histogram(totals_arr, bins=bins)
    x_centers = (edges[:-1] + edges[1:]) / 2.0
    labels = [f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges)-1)]

    colors = []
    for left, right in zip(edges[:-1], edges[1:]):
        if right <= user_score:
            colors.append("rgba(200,200,200,0.6)")
        else:
            colors.append("rgba(94,60,193,0.9)")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=x_centers, y=counts, marker_color=colors, width=bin_step*0.9,
                         hovertemplate="%{x:.0f} — %{y:,} thí sinh<extra></extra>"))

    # vertical line for user score
    fig.add_vline(x=user_score, line=dict(color="red", width=2, dash="dash"))
    # annotation
    y_annot = counts.max() * 0.85 if len(counts)>0 else 0
    fig.add_annotation(x=user_score, y=y_annot, text=f"<b>Điểm bạn: {user_score:.2f}</b>",
                       showarrow=True, arrowhead=2, ax=40, ay=-40, bgcolor="white")

    fig.update_layout(title=title, xaxis_title="Tổng điểm", yaxis_title="Số thí sinh",
                      template="plotly_white", bargap=0.02,
                      margin=dict(t=50, b=50, l=40, r=40))
    fig.update_xaxes(tickmode="array", tickvals=x_centers, ticktext=labels)
    return fig

def mini_bar_average(subjects, averages):
    """
    subjects: list of strings
    averages: list of floats
    """
    fig = go.Figure(go.Bar(x=subjects, y=averages, marker_color="rgba(94,60,193,0.9)"))
    fig.update_traces(texttemplate="%{y:.2f}", textposition="outside")
    fig.update_layout(title="Điểm trung bình theo môn", template="plotly_white",
                      yaxis=dict(range=[0,10]), margin=dict(t=40, b=80))
    return fig
