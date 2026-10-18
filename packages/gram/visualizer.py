# clx/gram/visualizer.py
"""
Lightweight CLX gram visualizer.

Design goals:
- Zero-noise, minimal deps (matplotlib only, networkx optional).
- Can be used headless (save to file) or interactive (show()).
- Stable API surface for future extension into richer dashboards.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple, Union

import matplotlib.pyplot as plt

try:
    import networkx as nx  # type: ignore
    _HAS_NX = True
except Exception:  # pragma: no cover
    _HAS_NX = False


Number = Union[int, float]


@dataclass
class NodeStyle:
    """Styling options for a single node."""
    size: int = 600
    color: str = "#1f77b4"
    alpha: float = 0.9


@dataclass
class EdgeStyle:
    """Styling options for a single edge."""
    width: float = 1.5
    color: str = "#555555"
    alpha: float = 0.7


@dataclass
class LayoutConfig:
    """Layout configuration for graph visualization."""
    seed: int = 42
    k: Optional[float] = None  # spring layout spacing
    scale: float = 1.0


class GramVisualizer:
    """
    Nano visualizer for CLX gram structures.

    This is intentionally minimal:
    - accepts generic node/edge lists
    - can overlay scalar scores (e.g., attention, activation, weight)
    - can render to screen or file
    """

    def __init__(
        self,
        layout: Optional[LayoutConfig] = None,
        default_node_style: Optional[NodeStyle] = None,
        default_edge_style: Optional[EdgeStyle] = None,
    ) -> None:
        self.layout = layout or LayoutConfig()
        self.default_node_style = default_node_style or NodeStyle()
        self.default_edge_style = default_edge_style or EdgeStyle()

    # --------------------------------------------------------------------- #
    # Core API
    # --------------------------------------------------------------------- #

    def plot_graph(
        self,
        nodes: Sequence[Union[str, int]],
        edges: Sequence[Tuple[Union[str, int], Union[str, int]]],
        node_scores: Optional[Dict[Union[str, int], Number]] = None,
        edge_scores: Optional[Dict[Tuple[Union[str, int], Union[str, int]], Number]] = None,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (8, 6),
        cmap: str = "viridis",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        Visualize a simple gram graph.

        Parameters
        ----------
        nodes:
            List of node identifiers.
        edges:
            List of (src, dst) tuples.
        node_scores:
            Optional scalar per node (e.g., activation, attention).
        edge_scores:
            Optional scalar per edge (e.g., weight, strength).
        title:
            Optional plot title.
        figsize:
            Matplotlib figure size.
        cmap:
            Colormap for scores.
        show:
            If True, call plt.show().
        save_path:
            If provided, save figure to this path.

        Returns
        -------
        fig:
            The created matplotlib Figure.
        """
        if not _HAS_NX:
            raise RuntimeError(
                "networkx is required for plot_graph(). "
                "Install with `pip install networkx`."
            )

        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        G.add_edges_from(edges)

        # layout
        pos = nx.spring_layout(
            G,
            seed=self.layout.seed,
            k=self.layout.k,
            scale=self.layout.scale,
        )

        fig, ax = plt.subplots(figsize=figsize)
        ax.set_axis_off()

        # node colors
        if node_scores:
            scores = [float(node_scores.get(n, 0.0)) for n in G.nodes()]
            vmin, vmax = min(scores), max(scores) if scores else (0.0, 1.0)
            nc = plt.cm.get_cmap(cmap)((scores - min(scores)) / (max(scores) - min(scores) or 1.0))  # type: ignore
        else:
            nc = self.default_node_style.color

        # edge widths
        if edge_scores:
            widths = [
                float(edge_scores.get((u, v), edge_scores.get((v, u), 1.0)))
                for u, v in G.edges()
            ]
        else:
            widths = self.default_edge_style.width

        nx.draw_networkx_nodes(
            G,
            pos,
            node_size=self.default_node_style.size,
            node_color=nc,
            alpha=self.default_node_style.alpha,
            ax=ax,
        )

        nx.draw_networkx_edges(
            G,
            pos,
            width=widths,
            edge_color=self.default_edge_style.color,
            alpha=self.default_edge_style.alpha,
            arrows=True,
            arrowstyle="-|>",
            ax=ax,
        )

        nx.draw_networkx_labels(G, pos, font_size=9, ax=ax)

        if title:
            ax.set_title(title)

        if save_path:
            fig.savefig(save_path, bbox_inches="tight", dpi=150)

        if show:
            plt.show()

        return fig

    def plot_sequence_scores(
        self,
        tokens: Sequence[str],
        scores: Sequence[Number],
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 2.5),
        cmap: str = "viridis",
        show: bool = False,
        save_path: Optional[str] = None,
    ) -> plt.Figure:
        """
        Visualize scalar scores over a token sequence (e.g., attention over time).

        Parameters
        ----------
        tokens:
            Sequence of token strings.
        scores:
            Scalar per token.
        title:
            Optional plot title.
        figsize:
            Matplotlib figure size.
        cmap:
            Colormap for bar colors.
        show:
            If True, call plt.show().
        save_path:
            If provided, save figure to this path.
        """
        if len(tokens) != len(scores):
            raise ValueError("tokens and scores must have the same length.")

        fig, ax = plt.subplots(figsize=figsize)

        scores_f = [float(s) for s in scores]
        vmin, vmax = min(scores_f), max(scores_f)
        norm = ( (s - vmin) / (vmax - vmin) ) if vmax != vmin else 0.5
        colors = plt.cm.get_cmap(cmap)(  # type: ignore
            [(float(s) - vmin) / (vmax - vmin or 1.0) for s in scores_f]
        )

        ax.bar(range(len(tokens)), scores_f, color=colors)
        ax.set_xticks(range(len(tokens)))
        ax.set_xticklabels(tokens, rotation=45, ha="right", fontsize=8)
        ax.set_ylabel("score")

        if title:
            ax.set_title(title)

        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, bbox_inches="tight", dpi=150)

        if show:
            plt.show()

        return fig


# ------------------------------------------------------------------------- #
# Convenience functions (functional style)
# ------------------------------------------------------------------------- #

_default_visualizer: Optional[GramVisualizer] = None


def get_default_visualizer() -> GramVisualizer:
    """Return a process-wide default visualizer instance."""
    global _default_visualizer
    if _default_visualizer is None:
        _default_visualizer = GramVisualizer()
    return _default_visualizer


def visualize_gram(
    nodes: Sequence[Union[str, int]],
    edges: Sequence[Tuple[Union[str, int], Union[str, int]]],
    node_scores: Optional[Dict[Union[str, int], Number]] = None,
    edge_scores: Optional[Dict[Tuple[Union[str, int], Union[str, int]], Number]] = None,
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = False,
) -> plt.Figure:
    """
    One-shot helper to visualize a gram graph with default settings.
    """
    viz = get_default_visualizer()
    return viz.plot_graph(
        nodes=nodes,
        edges=edges,
        node_scores=node_scores,
        edge_scores=edge_scores,
        title=title,
        save_path=save_path,
        show=show,
    )


def visualize_sequence_scores(
    tokens: Sequence[str],
    scores: Sequence[Number],
    title: Optional[str] = None,
    save_path: Optional[str] = None,
    show: bool = False,
) -> plt.Figure:
    """
    One-shot helper to visualize scores over a token sequence.
    """
    viz = get_default_visualizer()
    return viz.plot_sequence_scores(
        tokens=tokens,
        scores=scores,
        title=title,
        save_path=save_path,
        show=show,
    )
