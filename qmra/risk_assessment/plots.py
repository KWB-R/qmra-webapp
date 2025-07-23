from plotly import graph_objects as go
from plotly.offline import plot
from plotly import express as px
import pandas as pd

RISK_CATEGORY_BG_COLORS = dict(
    none='#E2FBAC', min='#FFDDB5', max='#FFECF4'
)
MAX_COLOR_SEQ = [
    "hsl(359, 100%, 40%)",
    "hsl(359, 100%, 60%)",
    "hsl(359, 100%, 80%)",
]

COLORS = {
    "Rotavirus": "hsl(332, 100, 49%)",
    "Campylobacter jejuni": "hsl(188, 100, 45%)",
    "Cryptosporidium parvum": "hsl(239, 100, 45%)",
}


def risk_plots(risk_assessment_results, output_type="div"):
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
            marker=dict(color=COLORS[r.pathogen]),
            hoverinfo="y"
        ))
        # infection_prob_fig.add_annotation(text=r.pathogen, showarrow=False, xref="paper", yref="paper", x=(i+1)/7, y=0)
        dalys_fig.add_trace(go.Box(
            x=["Minimum LRV", "Maximum LRV"],
            lowerfence=[r.dalys_minimum_lrv_min, r.dalys_maximum_lrv_min],
            upperfence=[r.dalys_minimum_lrv_max, r.dalys_maximum_lrv_max],
            q1=[r.dalys_minimum_lrv_q1, r.dalys_maximum_lrv_q1],
            q3=[r.dalys_minimum_lrv_q3, r.dalys_maximum_lrv_q3],
            median=[r.dalys_minimum_lrv_median, r.dalys_maximum_lrv_median],
            name=r.pathogen,
            marker=dict(color=COLORS[r.pathogen]),
            hoverinfo="y"
        ))
        # dalys_fig.add_annotation(text=r.pathogen, showarrow=False, xref="paper", yref="paper", x=(i+1)/7, y=0)

    infection_prob_fig.update_layout(
        boxmode='group',
        height=350,
        # font_family="Helvetica Neue, Helvetica, Arial, sans-serif",
        font_color="black",
        plot_bgcolor="#F6F6FF",
        xaxis=dict(title="", showgrid=False),
        yaxis=dict(title="Probability of infection per year",
                   showgrid=False),
        margin=dict(l=(int(output_type == "png") * 30), r=(int(output_type == "png") * 30), t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    infection_prob_fig.update_yaxes(type="log",
                                    showexponent='all',
                                    dtick=1,
                                    exponentformat='power'
                                    )
    infection_prob_fig.add_hline(y=0.0001, line_dash="dashdot",
                                 label=dict(
                                     text="tolerable risk level",
                                     textposition="end",
                                     yanchor="top",
                                     font=dict(color="#FF0000")
                                 ),
                                 line=dict(color="#FF0000", width=1)
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
        margin=dict(l=(int(output_type == "png") * 30), r=(int(output_type == "png") * 30), t=30, b=30),
        legend=dict(
            orientation="h",
            yanchor="top",
            xanchor="center",
            x=0.5,
        )
    )
    dalys_fig.update_yaxes(type="log",
                           showexponent='all',
                           dtick=1,
                           exponentformat='power'
                           )
    dalys_fig.add_hline(y=0.000001, line_dash="dashdot",
                        label=dict(
                            text="tolerable risk level",
                            textposition="end",
                            yanchor="top",
                            font=dict(color="#FF0000")
                        ),
                        line=dict(color="#FF0000", width=1)
                        )
    dalys_fig.update_traces(
        marker_size=8
    )
    if output_type == "div":
        return plot(infection_prob_fig, output_type="div", config={"displaylogo": False,
                                                                   "modeBarButtonsToRemove": ['zoom2d', 'pan2d',
                                                                                              'select2d', 'lasso2d',
                                                                                              'zoomIn2d', 'zoomOut2d',
                                                                                              'autoScale2d',
                                                                                              'resetScale2d']},
                    include_plotlyjs=False), \
            plot(dalys_fig, output_type="div", config={"displaylogo": False,
                                                       "modeBarButtonsToRemove": ['zoom2d', 'pan2d', 'select2d',
                                                                                  'lasso2d', 'zoomIn2d', 'zoomOut2d',
                                                                                  'autoScale2d', 'resetScale2d']},
                 include_plotlyjs=False)
    return infection_prob_fig.to_image(format=output_type), dalys_fig.to_image(format=output_type)
