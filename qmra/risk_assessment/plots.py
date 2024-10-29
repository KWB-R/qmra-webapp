from plotly import graph_objects as go
from plotly.offline import plot
from plotly import express as px
import pandas as pd

RISK_CATEGORY_BG_COLORS = dict(
    none='#E2FBAC', min='#FFDDB5', max='#FFECF4'
)
MAX_COLOR_SEQ = ["#FF0532",
                 "#FF506F",
                 "#FF8DA2"
                 ]

MIN_COLOR_SEQ = [
    "#FF873F",
    "#FFA570",
    "#ED5500"
]

NONE_COLOR_SEQ = [
    "#1B6638",
    "#46A16A",
    "#88D0A5"
]

COLOR_SEQS = dict(min=MIN_COLOR_SEQ, max=MAX_COLOR_SEQ, none=NONE_COLOR_SEQ)


def risk_plots(risk_assessment_results, risk_category="none"):
    infection_prob_fig = go.Figure()
    dalys_fig = go.Figure()
    for i, r in enumerate(risk_assessment_results):
        infection_prob_fig.add_trace(go.Box(
            x=["Minimum LRV", "Maximum LRV"],
            lowerfence=[r.infection_minimum_lrv_min, r.infection_maximum_lrv_min],
            upperfence=[r.infection_minimum_lrv_max, r.infection_maximum_lrv_max],
            q1=[r.infection_minimum_lrv_q1, r.infection_maximum_lrv_q1],
            q3=[r.infection_minimum_lrv_q3, r.infection_maximum_lrv_q3],
            median=[r.infection_minimum_lrv_median, r.infection_maximum_lrv_median],
            name=r.pathogen,
            marker=dict(color=COLOR_SEQS[r.infection_risk][i % 3])
        ))
        dalys_fig.add_trace(go.Box(
            x=["Minimum LRV", "Maximum LRV"],
            lowerfence=[r.dalys_minimum_lrv_min, r.dalys_maximum_lrv_min],
            upperfence=[r.dalys_minimum_lrv_max, r.dalys_maximum_lrv_max],
            q1=[r.dalys_minimum_lrv_q1, r.dalys_maximum_lrv_q1],
            q3=[r.dalys_minimum_lrv_q3, r.dalys_maximum_lrv_q3],
            median=[r.dalys_minimum_lrv_median, r.dalys_maximum_lrv_median],
            name=r.pathogen,
            marker=dict(color=COLOR_SEQS[r.dalys_risk][i % 3])
        ))

    infection_prob_fig.update_layout(
        boxmode='group',
        height=350,
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        plot_bgcolor="#F6F6FF",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Probability of infection per year",
                   showgrid=False),
        margin=dict(l=0, r=0, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    infection_prob_fig.update_yaxes(type="log")
    infection_prob_fig.add_hline(y=0.0001, line_dash="dashdot",
                                 label=dict(
                                     text="tolerable level",
                                     textposition="end",
                                     yanchor="top",
                                     font=dict(color="rgb(0, 3, 226)")
                                 ),
                                 line=dict(color="rgb(0, 3, 226)", width=3)
                                 )
    infection_prob_fig.update_traces(
        marker_size=8
    )

    dalys_fig.update_layout(
        boxmode='group',
        height=350,
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        plot_bgcolor="#F6F6FF",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="DALYs pppy", showgrid=False),
        margin=dict(l=0, r=0, t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    dalys_fig.update_yaxes(type="log")
    dalys_fig.add_hline(y=0.000001, line_dash="dashdot",
                        label=dict(
                            text="tolerable level",
                            textposition="end",
                            yanchor="top",
                            font=dict(color="rgb(0, 3, 226)")
                        ),
                        line=dict(color="rgb(0, 3, 226)", width=3)
                        )
    dalys_fig.update_traces(
        marker_size=8
    )

    return plot(infection_prob_fig, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False), \
        plot(dalys_fig, output_type="div", config={'displayModeBar': False}, include_plotlyjs=False)

